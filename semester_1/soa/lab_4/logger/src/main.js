const express = require('express');
const os = require('os');
const fs = require('fs');

const app = express();
const port = 3000;

app.get('/writeToFile', (req, res) => {
  const { data } = req.query;

  if (!data) {
    return res.status(400).json({ error: 'use param data to send data' });
  }
  const host = os.hostname();
  const content = `Host: ${host} data: ${data}\n`;
  fs.appendFile('logs.txt', content, (err) => {
    if (err) {
      return res.status(500).json({ error: 'Error.' });
    }

    return res.json({ message: 'Data was written.' });
  });
});

app.listen(port, () => {
  console.log(`Sever = http://localhost:${port}`);
});
