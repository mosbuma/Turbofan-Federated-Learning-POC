#!/bin/env python
"""
    Turbofan federated trainer
    Regularly check for new data in the grid and handle federated training and model serving.
"""
import atexit
import os
import argparse
from collections import defaultdict
import logging

import numpy as np
import termplotlib as tpl
import matplotlib.pyplot as plt
import matplotlib

import torch
import syft as sy
from apscheduler.schedulers.blocking import BlockingScheduler
from syft import PublicGridNetwork

from helper.data_helper import get_validation_data, get_test_data, WINDOW_SIZE
from helper.trainings_helper import data_result_size, start_federated_training, history
from helper.trainings_helper import get_model_error
from helper.turbofan_model import TurbofanModel

hook = sy.TorchHook(torch)

matplotlib.use("agg")

DATA_TAGS = ("#X", "#turbofan", "#dataset")
LABEL_TAGS = ("#Y", "#turbofan", "#dataset")
MODEL_ID = "turbofan"

grid_gateway_address = None
new_data_threshold = None
epochs = None
data_dir = None
model_dir = None

training_rounds = 0
inputs_used = defaultdict(list)
labels_used = defaultdict(list)


parser = argparse.ArgumentParser(description="Run Federated Trainer.")

parser.add_argument(
    "--grid_gateway_address",
    type=str,
    help="Address used to contact the Grid Gateway. Default is os.environ.get('GRID_GATEWAY_ADDRESS', None).",
    default=os.environ.get("GRID_GATEWAY_ADDRESS", None),
)

parser.add_argument(
    "--new_data_threshold",
    type=str,
    help="Threshold for the amount of new data windows needed to start a new federated learning round', 1000).",
    default=os.environ.get("NEW_DATA_THRESHOLD", 1000),
)

parser.add_argument(
    "--scheduler_interval",
    type=str,
    help="Interval for the scheduler to check for new data in seconds.', 10).",
    default=os.environ.get("SCHEDULER_INTERVAL", 10),
)

parser.add_argument(
    "--epochs",
    type=str,
    help="Epochs to run when doing federated learning.', 100).",
    default=os.environ.get("EPOCHS", 100),
)

parser.add_argument(
    "--data_dir",
    type=str,
    help="The directory of the data to use.",
    default=os.environ.get("DATA_DIR", None),
)

parser.add_argument(
    "--model_dir",
    type=str,
    help="The directory for the models.",
    default=os.environ.get("MODEL_DIR", None),
)


def handle_interval():
    """Check the grid for enough new data and then start a new training round."""
    global training_rounds

    inputs, labels = get_grid_data()
    inputs, labels = filter_new_data(inputs, labels)
    data_count = data_result_size(list(inputs.values()))
    print("Found {} new input samples in the grid".format(data_count))

    if data_count >= new_data_threshold:
        print("Enough data available, starting training...")
        # enough new data is available, let´s start a new round of federated training
        training_rounds += 1
        start_training_round(inputs, labels)


def get_grid_data():
    """Retrieve all data from the grid.

    :return: A tuple with the input data and labels from the grid
    """
    grid = PublicGridNetwork(hook, "http://{}".format(grid_gateway_address))
    inputs = grid.search(*DATA_TAGS)
    labels = grid.search(*LABEL_TAGS)

    return inputs, labels


def filter_new_data(inputs, labels):
    """Filter data that was already used in earlier training rounds.

    :param inputs: Input to filter
    :param labels: Labels to filter
    :return: A tuple with the filtered inputs and labels
    """
    inputs_filtered = defaultdict(list)
    labels_filtered = defaultdict(list)

    for node in inputs:
        for pointer in inputs[node]:
            if pointer.id_at_location not in inputs_used[node]:
                inputs_filtered[node].append(pointer)
    for node in labels:
        for pointer in labels[node]:
            if pointer.id_at_location not in labels_used[node]:
                labels_filtered[node].append(pointer)

    return inputs_filtered, labels_filtered


def remember_data_used(inputs, labels):
    """Add the given inputs and labels to global dictionaries to filter them in later training rounds.

    :param inputs: Inputs already used in training
    :param labels: Labels already used in training
    """
    for node in inputs:
        for pointer in inputs[node]:
            inputs_used[node].append(pointer.id_at_location)
    for node in labels:
        for pointer in labels[node]:
            labels_used[node].append(pointer.id_at_location)


def save_model(model):
    """Save a torch model to disk.

    :param model: Model to save
    """
    torch.save(model, "{}/turbofan_{}.pt".format(model_dir, training_rounds))


def load_initial_model():
    """Load the model from the initial training from disk.

    :return: The initial model
    """
    return torch.load("{}/turbofan_initial.pt".format(model_dir))


def load_latest_model():
    """Load the latest model created during federated learning from disk.

    :return: The latest model
    """
    index = training_rounds - 1
    if index == 0:
        index = "initial"
    return torch.load("{}/turbofan_{}.pt".format(model_dir, index))


def serve_model(model):
    """Serve the model to the grid.

    :param model: Model to serve
    """
    trace_model = torch.jit.trace(model, torch.rand((1, WINDOW_SIZE, 11)))

    print(
        "Creating public gateway on ",
        "http://{}".format(grid_gateway_address),
        flush=True,
    )
    grid = PublicGridNetwork(hook, "http://{}".format(grid_gateway_address))

    # note: the current implementation only returns the first node found
    node = grid.query_model_hosts(MODEL_ID)
    if node:
        print("Replacing existing model on node", node, flush=True)
        # the model was already deployed, delete it before serving
        node.delete_model(MODEL_ID)
        node.serve_model(trace_model, model_id=MODEL_ID, allow_remote_inference=True)
    else:
        print("start Serve Model", flush=True)
        grid.serve_model(trace_model, id=MODEL_ID, allow_remote_inference=True)

    # Get the list of connected nodes
    # response = grid._ask_gateway("GET", "get-all-nodes")

    # Print the connected nodes
    # for node_id, node_info in response.items():
    #     print(f"Node ID: {node_id}, Node address: {node_info['address']}", flush=True)


def plot_history(rmse):
    """Plot the train and validation loss to an image and to the console.

    :param rmse: The RMSE score to print in the image
    """
    plt.figure()
    plt.xlabel("Epoch")
    plt.plot(history["epoch"], np.array(history["loss"]), label="Train Loss")
    plt.plot(history["epoch"], np.array(history["val_loss"]), label="Validation loss")
    plt.legend()
    plt.title("RMSE: {:7.2f}".format(rmse))
    plt.savefig("{}/turbofan_fl_loss_{}.png".format(model_dir, training_rounds))

    # plot to console
    fig = tpl.figure()
    fig.plot(
        np.array(history["epoch"]),
        np.array(history["loss"]),
        label="Train Loss",
        xlabel="Epoch",
    )
    fig.plot(
        np.array(history["epoch"]),
        np.array(history["val_loss"]),
        label="Validation loss",
        xlabel="Epoch",
    )
    fig.show()


def start_training_round(inputs, labels):
    """Start a new federated training round.

    :param inputs: The inputs from the grid
    :param labels: The labels from the grid
    """
    inputs_list = list(inputs.values())
    labels_list = list(labels.values())
    val_data, val_labels = get_validation_data(data_dir)
    latest_model = load_latest_model()
    model = start_federated_training(
        latest_model, inputs_list, labels_list, val_data, val_labels, epochs
    )

    # evaluate model
    test_data, test_labels = get_test_data(data_dir)
    rmse = get_model_error(model, test_data, test_labels)
    print("Model RMSE is {:7.2f}".format(rmse))

    plot_history(rmse)

    print("Serving the updated model...")
    serve_model(model)
    save_model(model)

    remember_data_used(inputs, labels)


if __name__ == "__main__":
    args = parser.parse_args()

    # read in the arguments
    grid_gateway_address = args.grid_gateway_address
    new_data_threshold = int(args.new_data_threshold)
    scheduler_interval = int(args.scheduler_interval)
    epochs = int(args.epochs)
    data_dir = args.data_dir
    model_dir = args.model_dir

    logging.getLogger("apscheduler").setLevel(logging.ERROR)

    print("Deploying initial model to grid...")

    initial_model = load_initial_model()
    print("***** loaded initial model")
    serve_model(initial_model)

    print("Started Federated Trainer... watching for new data.")

    scheduler = BlockingScheduler(daemon=True)
    scheduler.add_job(handle_interval, "interval", args=[], seconds=scheduler_interval)

    # Shut down the scheduler when exiting
    atexit.register(lambda: scheduler.shutdown())

    scheduler.start()
