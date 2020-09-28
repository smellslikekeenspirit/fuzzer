# fuzzer
fuzz-testing tool for exploring vulnerabilities in DVWA

[Setup: Install XAMPP and DVWA](https://e3fi389.wordpress.com/2017/09/17/how-to-setup-dvwa-using-windows-xampp/)

To run the scripts, please use explicit specifiers for each argument, i.e.

`python3 fuzz.py --command=discover --url=http://localhost/ --custom-auth=dvwa`

instead of

`python3 fuzz.py discover http://localhost/ --custom-auth=dvwa`

If custom-auth is not given, the script assumes it will run fuzzer-tests, i.e.

`python3 fuzz.py --command=discover --url=http://127.0.0.1/fuzzer-tests`

