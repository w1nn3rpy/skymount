import paramiko
import re

setup_outline_command = 'sudo bash -c "$(wget -qO- https://raw.githubusercontent.com/Jigsaw-Code/outline-server/master/src/server_manager/install_scripts/install_server.sh)"'


def execute_outline_server(host, port, user, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(host, port, user, password)

        ### Установка docker ###
        ssh.exec_command('curl https://get.docker.com/ | sh')

        stdin, stdout, stderr = ssh.exec_command(setup_outline_command)

        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        ssh.close()

        return output, error

    except Exception as e:
        return None, str(e)

def get_data_from_output(output: str):
    # Извлекаем данные с помощью регулярных выражений
    api_url = re.search(r'"apiUrl":"(.*?)"', output).group(1)
    cert_sha256 = re.search(r'"certSha256":"(.*?)"', output).group(1)
    management_port = re.search(r'Management port (\d+)', output).group(1)
    access_key_port = re.search(r'Access key port (\d+)', output).group(1)

    return api_url, cert_sha256, management_port, access_key_port