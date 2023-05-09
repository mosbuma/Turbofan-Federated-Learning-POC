const express = require('express');
const bodyParser = require('body-parser');
const bearerToken = require('express-bearer-token');

const app = express();
app.use(bodyParser.json());
app.use(bearerToken());

// Define a static collection of users and their valid bearer tokens
const users = [
  {
    name: 'User 1',
    id: 1,
    tokens: ['abc123', 'def456'],
  },
  {
    name: 'User 2',
    id: 2,
    tokens: ['xyz789', 'uvw987'],
  },
];

app.post('/api/isJobAllowed', async (req, res) => {
  const url = req.body.url;
  const bearerToken = req.token;
  console.log('got body fields:', Object.keys(req.body));
  console.log('got bearertoken', bearerToken);

  // Check if the bearer token is valid for any of the users
  let userName = '';
  for (const user of users) {
    if (user.tokens.includes(bearerToken)) {
      userName = user.name;
      break;
    }
  }

  if (userName === '') {
    // If the bearer token is not valid for any user, return an error message
    res.status(401).send('Unauthorized');
    return;
  }

  // If the bearer token is valid for a user, make the REST API call with the bearer token
  try {
    res.json({ allowed: true, userName, responseData: { somedata: true } });
  } catch (error) {
    console.error(error);
    res.status(500).send('Error making REST API call');
  }
});

const port = 8081;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
