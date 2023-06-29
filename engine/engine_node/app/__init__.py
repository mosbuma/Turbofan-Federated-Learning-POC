import logging
import datetime
import os

from flask import Flask
import syft as sy
import torch as th
import pandas as pd

from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from syft import PublicGridNetwork
from syft.workers.node_client import NodeClient

from apscheduler.schedulers.gevent import GeventScheduler
import atexit

from .main import html
from .main import db
from .main.persistence.utils import set_database_config
from .main.handler import sensor_handler
from .main.handler.sensor_handler import handle_current_sensors
from .main.handler.sensor_handler import handle_all_data_fast
from .main.helper import config_helper

from .main.helper import data_helper

from .main.handler.sensor_handler import move_current_data_to_training

hook = sy.TorchHook(th)

shared_data = []
shared_labels = []

def create_app(
    engine_id,
    grid_node_address,
    grid_gateway_address,
    data_dir,
    dataset_id,
    cycle_length,
    debug=False,
    test_config=None,
):
    """Create / Configure flask socket application instance.

    Args:
        engine_id : The id of this engine.
        grid_node_address : The address of the local grid node to connect.
        grid_gateway_address : The address of the grid gateway.
        data_dir : The directory containing the engine data.
        dataset_id : The id of the worker dataset to use.
        cycle_length : The length of one engine cycle.
        debug (bool) : debug flag.
        test_config (bool) : Mock database environment.
    Returns:
        app : Flask application instance.
    """
    app = Flask(__name__)
    app.debug = debug
    app.config["SECRET_KEY"] = "justasecretkeythatishouldputhere"

    # Register app blueprints
    app.register_blueprint(html, url_prefix=r"/")

    # Set SQLAlchemy configs
    app = set_database_config(app, test_config=test_config)
    app.app_context().push()
    db.drop_all()
    db.create_all()

    config_helper.engine_id = engine_id
    config_helper.grid_node_address = grid_node_address
    config_helper.grid_gateway_address = grid_gateway_address
    config_helper.data_dir = data_dir
    config_helper.dataset_id = dataset_id

    print("Creating Grid Node...", flush=True)
    
    # path = "/data/train_FD001.txt"
    path = f"/data/node_dataset_{engine_id}.txt"

    jet_data = pd.read_csv(path, sep=" ", header=None)
    jet_data.columns = ["id","cycle","op1","op2","op3","sensor1","sensor2","sensor3","sensor4","sensor5"
                        ,"sensor6","sensor7","sensor8","sensor9","sensor10","sensor11","sensor12","sensor13"
                        ,"sensor14","sensor15","sensor16","sensor17","sensor18","sensor19"
                        ,"sensor20","sensor21"]

    jet_id_and_rul = jet_data.groupby(['id'])[["id" ,"cycle"]].max()
    jet_id_and_rul.set_index('id', inplace=True)

    jet_data = data_helper.RUL_calculator(jet_data, jet_id_and_rul)

    jet_relevant_data = jet_data.drop(["op1", "op2", "op3", "sensor1", "sensor5", "sensor6", "sensor10", "sensor15", "sensor16", "sensor18", "sensor19", "sensor20", "sensor21"], axis=1)

    # Use a scaler to make values of all data attributes within the same range of 0 to 1
    #This can help increase accuracy of the model
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(jet_relevant_data.drop(['id', 'RUL'], axis=1))
    scaled_features = pd.DataFrame(scaled_features, columns = jet_relevant_data.drop(['id', 'RUL'], axis = 1).columns)

    scaled_features['id'] = jet_relevant_data['id']
    scaled_features['RUL'] = jet_relevant_data['RUL']

    # print(scaled_features.head())

    data = scaled_features.copy()

    # ???
    cycle=30
    data['label'] = data['RUL'].apply(lambda x: 1 if x <= cycle else 0)

    # y_df is the ground truth values for the dataset, essentially telling the model what is correct
    # More or less y_df is "labels" and x_df is "inputs"
    y_df = data['label']
    X_df = data.drop(['RUL', 'id', 'label'], axis=1)

    X_train, X_test, y_train, y_test = train_test_split(X_df, y_df, test_size=0.2, random_state=3)

    # print(X_train.shape)
    # print(X_test.shape)

    X = X_train.values
    y = y_train.values

    # Convert the data to PyTorch tensors
    X = th.tensor(X, dtype=th.float32)
    y = th.tensor(y, dtype=th.float32)

    y = y.view(-1, 1)

    # tag the data so it can be searched within the grid
    X = X.tag("#X", "#dataset").describe(
        f"The input datapoints for the {engine_id} dataset"
    )
    y = y.tag("#Y", "#dataset").describe(
        f"The input labels for the {engine_id} dataset"
    )

    grid_node = NodeClient(
        hook, address="ws://{}".format(config_helper.grid_node_address)
    )

    print("GRID NODE : ", grid_node, flush=True)

    shared_data.append(X.send(grid_node))
    shared_labels.append(y.send(grid_node))

    print(engine_id, " has uploaded their data....", flush=True)

    # -----------------------------------------------------------------

    # grid = PublicGridNetwork(hook, "http://{}".format(grid_gateway_address))
    # results = grid.search("#X", "#dataset")
    # print(results, flush=True)

    # -----------------------------------------------------------------

    # # data preprocessing for training
    # new_train_data = data_helper.add_rul_to_train_data(new_train_data)
    # data_helper.drop_unnecessary_columns(new_train_data)
    # x_train_new, y_train_new = data_helper.transform_to_windowed_data(
    #     new_train_data, with_labels=True
    # )
    # y_train_new = data_helper.clip_rul(y_train_new)

    # # transform to torch tensors
    # tensor_x_train_new = th.Tensor(x_train_new)
    # tensor_y_train_new = th.Tensor(y_train_new)

    # # tag the data so it can be searched within the grid
    # tensor_x_train_new = tensor_x_train_new.tag("#X", "#turbofan", "#dataset").describe(
    #     "The input datapoints to the turbofan dataset."
    # )
    # tensor_y_train_new = tensor_y_train_new.tag("#Y", "#turbofan", "#dataset").describe(
    #     "The input labels to the turbofan dataset."
    # )

    # grid_node = NodeClient(
    #     hook, address="ws://{}".format(config_helper.grid_node_address)
    # )

    # print("GRID NODE : ", grid_node, flush=True)

    # x_pointer = tensor_x_train_new.send(grid_node)
    # y_pointer = tensor_y_train_new.send(grid_node)

    # print("Data Pointers : ", x_pointer, y_pointer, flush=True)

    return app

# def start_fast_simulation(app, start_delay_seconds):
#     logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)

#     scheduler = GeventScheduler(daemon=True, timezone="Etc/UTC")
#     run_date = datetime.datetime.now() + datetime.timedelta(seconds=start_delay_seconds)
        
#     scheduler.add_job(handle_all_data_fast, "date", args=[app], run_date=run_date)
#     scheduler.start()

#     # Shut down the scheduler when exiting the app
#     atexit.register(lambda: scheduler.shutdown())


# def start_sensor_scheduler(app, cycle_length):
#     """Start a scheduler to regularly read in and save the current sensor data.

#     :param app: The app context
#     :param cycle_length: The length of one cycle in seconds
#     :return: None
#     """

#     logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)

#     scheduler = GeventScheduler(daemon=True, timezone="Etc/UTC")
#     scheduler.add_job(
#         handle_current_sensors, "interval", args=[app, scheduler], seconds=cycle_length
#     )

#     scheduler.start()

#     # Shut down the scheduler when exiting the app
#     atexit.register(lambda: scheduler.shutdown())
