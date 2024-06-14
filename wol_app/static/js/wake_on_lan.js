document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('wolForm');
    const macAddressInput = document.getElementById('mac_address');
    const ipAddressInput = document.getElementById('ip_address');
    const portInput = document.getElementById('port');
    const messageDiv = document.getElementById('message');
    const cmdFileList = document.getElementById('cmdFileList');
    const cmdFilesSelect = document.getElementById('cmdFiles');
    const executeCmdBtn = document.getElementById('executeCmdBtn');
    const checkHostStatusInterval = 5000;
    let checkHostStatusTimer;

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        disableForm();
        sendWakeOnLanRequest();
    });

    executeCmdBtn.addEventListener('click', function () {
        executeSelectedCmd();
    });

    function disableForm() {
        macAddressInput.disabled = true;
        ipAddressInput.disabled = true;
        portInput.disabled = true;
        form.querySelector('button').disabled = true;
        form.querySelector('button').style.backgroundColor = 'grey';
    }

    function enableForm() {
        macAddressInput.disabled = false;
        ipAddressInput.disabled = false;
        portInput.disabled = false;
        form.querySelector('button').disabled = false;
        form.querySelector('button').style.backgroundColor = '';
    }

    function sendWakeOnLanRequest() {
        const data = {
            mac_address: macAddressInput.value,
            ip_address: ipAddressInput.value,
            port: parseInt(portInput.value, 10)
        };

        fetch('/api/wake_and_check/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                messageDiv.textContent = data.message;
                checkHostStatus();
            } else {
                messageDiv.textContent = data.message;
                enableForm();
            }
        })
        .catch(error => {
            messageDiv.textContent = 'An error occurred: ' + error;
            enableForm();
        });
    }

    function checkHostStatus() {
        const ipAddress = ipAddressInput.value;
        let secondsWaited = 0;

        checkHostStatusTimer = setInterval(() => {
            fetch('/api/check_host_up/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ ip_address: ipAddress })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    clearInterval(checkHostStatusTimer);
                    messageDiv.textContent = 'Host is up. Fetching command files...';
                    fetchCmdFiles();
                } else {
                    secondsWaited += checkHostStatusInterval / 1000;
                    messageDiv.textContent = `Checking host status... (Waited ${secondsWaited} seconds)`;
                }
            })
            .catch(error => {
                clearInterval(checkHostStatusTimer);
                messageDiv.textContent = 'An error occurred: ' + error;
                enableForm();
            });
        }, checkHostStatusInterval);
    }

    function fetchCmdFiles() {
        fetch('/api/get_cmd_files/')
            .then(response => response.json())
            .then(data => {
                if (data.cmd_files.length > 0) {
                    data.cmd_files.forEach(file => {
                        const option = document.createElement('option');
                        option.value = file;
                        option.textContent = file;
                        cmdFilesSelect.appendChild(option);
                    });
                    cmdFileList.style.display = 'block';
                } else {
                    messageDiv.textContent = 'No .cmd files found.';
                }
            })
            .catch(error => {
                messageDiv.textContent = 'An error occurred: ' + error;
                enableForm();
            });
    }

    function executeSelectedCmd() {
        const selectedCmdFile = cmdFilesSelect.value;

        fetch('/api/execute_cmd/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ file_name: selectedCmdFile })
        })
        .then(response => response.json())
        .then(data => {
            messageDiv.textContent = data.message;
            if (data.success) {
                messageDiv.textContent = 'Execution completed successfully.';
                enableForm();
                cmdFileList.style.display = 'none';
            } else {
                messageDiv.textContent = 'Execution failed.';
                enableForm();
            }
        })
        .catch(error => {
            messageDiv.textContent = 'An error occurred: ' + error;
            enableForm();
        });
    }
});
