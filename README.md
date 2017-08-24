# trytravis

[![Travis](https://img.shields.io/travis/SethMichaelLarson/trytravis/master.svg?style=flat)](https://travis-ci.org/SethMichaelLarson/trytravis)
[![AppVeyor](https://img.shields.io/appveyor/ci/SethMichaelLarson/trytravis/master.svg?style=flat)](https://travis-ci.org/SethMichaelLarson/trytravis)
[![Codecov](https://img.shields.io/codecov/c/github/SethMichaelLarson/trytravis/master.svg?style=flat)](https://codecov.io/gh/SethMichaelLarson/trytravis)
[![BountySource](https://img.shields.io/badge/donate-bountysource-brightgreen.svg?style=flat)](https://salt.bountysource.com/teams/trytravis)

Send your local git repository to Travis CI without needless commits and pushes.

## About

- Have you ever spent hours committing tiny changes, pushing, waiting for a specific job over and over again?
- Do your Pull Requests have 5 times as many commits as there are meaningful changes simply due to CI issues?
- Tired of complicated `git` commands in order to roll-back and delete useless commits from your history?

If any of these are true, `trytravis` is the tool for you.

## Installation and Usage

Here's a short guide on how to get started. If you've got questions or need
a clarification on any steps don't hesitate to open an issue. (Or one better,
open a Pull Request to fix the problem!)

### Supported Platforms

`trytravis` works on Linux, Windows, and Mac OS and only requires
Python 2.7 or Python 3.3 or later to be installed to run.

### Install the latest `trytravis` via [`pip`](https://pip.pypa.io/en/stable/):
```
bash-4.4$ pip install trytravis
bash-4.4$ trytravis --version
1.0.0
```

### Optional: [Create a new GitHub account](https://help.github.com/articles/signing-up-for-a-new-github-account/).

Create the GitHub account, make sure you use an email address that you
can verify as that is required in order to create a Personal Access Token.
Also register the account with Travis. You shouldn't have to log into this
account again after finishing this tutorial but hang on to the credentials
just in case.

You can use your own GitHub account if you want as well.

### [Create a GitHub repository](https://github.com/new) called '`trytravis`'.

**IMPORTANT:** The repository *MUST* be named exactly `trytravis`. If the repository
is not named this way then the tool won't function properly. The repository can be private
and it is encouraged to be private if you plan on using the tool for working on private
projects.

Here's a [guide on how to create a GitHub repository](https://help.github.com/articles/create-a-repo/).
Don't use an organization account as the owner of the repository.
Use the same account that you used to create this repository for the next step.

### Create a [Personal Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) for your GitHub account.

After you've creating an access token copy it and then run the following command:

```
bash-4.4$ trytavis token
Enter your personal access token: 
```

Copy the personal access token and paste it into the input and press Enter.
To view or stop this from being used it can be found in the directory `~/.config/trytravis`
on Linux and `C:\Users\[USERNAME]\trytravis` on Windows.

### [Register the `trytravis` repository with Travis CI](https://docs.travis-ci.com/user/getting-started/)

Remember the repository should be named `trytravis` and that you should use your
newly created user if you decided to create one.

### Ready to Use the Tool!

Move to the base directory of your project and execute the following command:

  ```
  bash-4.4$ trytravis
  ```

After this if `trytravis` is able to detect your GitHub repository and local changes
you should see the following output from this command:

```
Submitting your project...ok
Waiting for a Travis build to start...ok

Your build number is: 1234567
Your build can be found here: https://travis-ci.org/trytravis-1/trytravis/1234567

#1  ✔ linux c python 2.7 TOXENV=lint
#2  ✔ linux c python 3.6 TOXENV=lint
#3  ✕ linux s python 2.7 TOXENV=py27
#4  ✔ linux c python 3.4 TOXENV=py34
#5  ✔ linux c python 3.5 TOXENV=py35
#6  ● linux s python 3.6 TOXENV=py36
#7  ●  osx  s python 2.7 TOXENV=py27
#8  ●  osx  c python 3.4 TOXENV=py34
#9  ●  osx  c python 3.5 TOXENV=py35
#10 ●  osx  s python 3.6 TOXENV=py36
```

## Contributing

There are many ways to contribute to `trytravis`, even if you are not skilled in Python programming
including: Contributing financially via [BountySource](https://salt.bountysource.com/teams/trytravis),
opening pull requests, raising issues, updating documentation, spreading the word via social media,
and more! Check out [`CONTRIBUTING.md`](https://github.com/SethMichaelLarson/trytravis/blob/master/CONTRIBUTING.md)
for more information and guidelines to contributing.

## License

This project is licensed under `Apache-2.0`. Read [`LICENSE`](https://github.com/SethMichaelLarson/trytravis/blob/master/LICENSE) for more information.

```
 Copyright 2017 Seth Michael Larson

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
limitations under the License.
```

## Author

Follow me on Twitter [`@pythoasis`](https://twitter.com/pythoasis)
for updates on `trytravis` and other projects that I'm working on.
