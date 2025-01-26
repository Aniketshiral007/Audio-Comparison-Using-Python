const { exec } = require('child_process');

// Command to navigate to the directory, activate the virtual environment, and keep the shell running
const command = 'bash -c "cd /home/india/audiofinal && source myenv/bin/activate && exec bash"';

const child = exec(command, { shell: '/bin/bash' }, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }

  if (stderr) {
    console.error(`Stderr: ${stderr}`);
    return;
  }

  console.log(`Stdout: ${stdout}`);
});

child.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

child.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

child.on('close', (code) => {
  console.log(`Child process exited with code ${code}`);
});

