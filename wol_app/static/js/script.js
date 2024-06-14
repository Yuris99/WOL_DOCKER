function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('wolForm').addEventListener('submit', function(event) {
        event.preventDefault();

        const macAddressInput = document.getElementById('mac_address');
        const ipAddressInput = document.getElementById('ip_address');
        const portInput = document.getElementById('port');
        const messageDiv = document.getElementById('message');
        const submitButton = event.target.querySelector('button[type="submit"]');
        const formData = new FormData(this);

        macAddressInput.classList.remove('error');
        ipAddressInput.classList.remove('error');
        portInput.classList.remove('error');
        messageDiv.textContent = 'Checking host status...';
        messageDiv.classList.remove('error-message');

        // 비활성화 submit 버튼
        submitButton.disabled = true;
        submitButton.style.backgroundColor = '#cccccc';

        fetch('/api/wake_and_check/', {
            method: 'POST',
            body: JSON.stringify({
                mac_address: macAddressInput.value,
                ip_address: ipAddressInput.value,
                port: parseInt(portInput.value)
            }),
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            submitButton.disabled = false; // 응답을 받은 후 submit 버튼 활성화
            submitButton.style.backgroundColor = ''; // 기본 색상으로 변경

            if (data.success) {
                if (data.message === 'The computer is already on.') {
                    messageDiv.textContent = data.message;
                } else {
                    messageDiv.textContent = data.message;
                    // Disable input boxes and hide the submit button
                    macAddressInput.disabled = true;
                    ipAddressInput.disabled = true;
                    portInput.disabled = true;
                    submitButton.style.display = 'none';

                    let secondsWaited = 0;
                    const interval = setInterval(() => {
                        secondsWaited++;
                        messageDiv.textContent = `Waiting for ${secondsWaited} seconds...`;
                    }, 1000); // 1 second interval for counting

                    const checkHostUp = setInterval(() => {
                        fetch('/api/check_host_up/', {
                            method: 'POST',
                            body: JSON.stringify({
                                ip_address: ipAddressInput.value
                            }),
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRFToken': getCookie('csrftoken')
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                clearInterval(interval);
                                clearInterval(checkHostUp);
                                messageDiv.textContent = 'Host is up!';
                            }
                        })
                        .catch(error => {
                            messageDiv.textContent = 'An error occurred while checking host status: ' + error;
                            messageDiv.classList.add('error-message');
                        });
                    }, 5000); // 5 seconds interval for ping

                    setTimeout(() => {
                        clearInterval(interval);
                        clearInterval(checkHostUp);
                    }, 50000);
                }
            } else {
                messageDiv.textContent = data.message;
                messageDiv.classList.add('error-message');
                if (data.errors && data.errors.mac_address) {
                    macAddressInput.classList.add('error');
                }
                if (data.errors && data.errors.ip_address) {
                    ipAddressInput.classList.add('error');
                }
                if (data.errors && data.errors.port) {
                    portInput.classList.add('error');
                }
            }
        })
        .catch(error => {
            submitButton.disabled = false; // 오류 발생 시 submit 버튼 활성화
            submitButton.style.backgroundColor = ''; // 기본 색상으로 변경
            messageDiv.textContent = 'An error occurred: ' + error;
            messageDiv.classList.add('error-message');
        });
    });
});
