# Penalty Party Contribution Guide:
Thanks for being interested in contributing to PenaltyParty! 

# Development Environment: Quickstart Guide:
## VSCode Development Environment:
If you're working on PenaltyParty it can be useful to set up a local database such that you can test your changes locally. Here's how to set that up:
1. Make sure you've cloned this repository, and are branching from the latest develop.
2. Install the [Dev Containers Extension]("https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers").
3. Bring up the command palette with `CTRL + P`, and select `Dev Containers: Open Folder in Container` when prompted. 
4. Once you're attached to the container, create a Django superuser for the development with `python manage.py createsuperuser`
5. Start the development server by running `./docker-startup.sh`
6. Note that the dev database isn't automatically populated, but that you can add questions via the Django admin interface. 

# Short FAQ:
## How do I report a bug?
Make an issue for us, on this repository! Feel free to also open issues if you have other problems with PenaltyParty, or if you have any feature requests.
Please check whether the issue that you're trying to create does not already exist in the [issue tracker](https://github.com/mxsasha/penaltyparty/issues).
We'll try to get back to you as soon as possible, but we're volunteers that work on this in our spare time. 

## I want to write questions
The "Suggest a question interface" is on [the Roadmap](https://github.com/mxsasha/penaltyparty/milestone/2) and is coming soon! 

## I think this question is wrong!
Open an issue and we will get one of our question writers to look at it again! 
It helps if you can tell us what exactly is wrong with the question, and reference specific sections of the WFTDA Rules/cases.

# Notes on style:
The only formatter we _particularly_ enforce is the use of `djLint` for formatting the HTML templates. 
Please don't use other HTML linters or formatters, as they don't account for the Django template language.

# Code of Conduct:
We follow the [WFTDA Code of Conduct](https://static.wftda.com/files/wftda-code-of-conduct.pdf).