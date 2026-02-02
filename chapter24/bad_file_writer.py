#!/usr/bin/env python3
"""
BAD CODE EXAMPLE - FOR EDUCATIONAL PURPOSES ONLY
This code demonstrates common anti-patterns and security issues.
DO NOT RUN THIS CODE!
"""

import os

def write_to_file(file_path):

    evaluated_path = eval(f"'{file_path}'")

    file = open(evaluated_path, 'w')
    

    secret_key = "myuselesssecretjustfordemo"
    

    file.write("hello from me")
    

    print(f"Wrote to file: {evaluated_path} using key: {secret_key}")



user_input = input("Enter file path: ")


write_to_file(user_input)
