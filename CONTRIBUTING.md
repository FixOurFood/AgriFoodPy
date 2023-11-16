# Contributor Guidelines

How to contribute
-----------------
AgriFoodPy is open source, built on open source, and we'd love to have you hang
out in our community.
Whether you would like to contribute to AgriFoodPy with your own piece of code
or helping develop a concrete feature in AgriFoodPy:

1. Read through our [Discussions Page](https://github.com/FixOurFood/AgriFoodPy/discussions)
to start a new conversation and share your ideas or follow up an existing
conversation on a particular feature.

1. Following the discussions, when you have a good idea of the specifics 
of the feature you wish to contribute, open an
[Issue](https://github.com/FixOurFood/AgriFoodPy/issues) describing the feature. 

1. Then follow the `Contributor Guidelines` on the rest of this page to open
a [Pull Request](https://github.com/FixOurFood/AgriFoodPy/pulls)
to contribute the code implementing the new feature.

## GitHub Workflow

### Fork and Clone the AgriFoodPy Repository.

**You should only need to do this step once**

First *fork* the AgriFoodPy repository. A fork is your own remote copy of the
repository on GitHub. To create a fork:

  1. Go to the [AgriFoodPy GitHub Repository](https://github.com/FixOurFood/AgriFoodPy)
  2. Click the **Fork** button (in the top-right-hand corner)
  3. Choose where to create the fork, typically your personal GitHub account

Next *clone* your fork. Cloning creates a local copy of the repository on your
computer to work with. To clone your fork:

```bash
   git clone https://github.com/<your-account>/AgriFoodPy.git
```

Finally add the ``agrifoodpy`` repository as a *remote*. This will allow you to
fetch changes made to the codebase. To add the ``agrifoodpy`` remote:

```bash
  cd AgriFoodPy
  git remote add afp https://github.com/FixOurFood/AgriFoodPy.git
```

### Create a branch for your new feature

Create a *branch* off the ``agrifoodpy`` main branch. Working on unique branches
for each new feature simplifies the development, review and merge processes by
maintining logical separation. To create a feature branch:

```bash
  git fetch agrifoodpy
  git checkout -b <your-branch-name> agrifoodpy/main
```

### Hack away!

Write the new code you would like to contribute and *commit* it to the feature
branch on your local repository. Ideally commit small units of work often with
clear and descriptive commit messages describing the changes you made.
To commit changes to a file:

```bash
  git add file_containing_your_contribution
  git commit -m 'Your clear and descriptive commit message'
```

*Push* the contributions in your feature branch to your remote fork on GitHub:

```bash
  git push origin <your-branch-name>
```

**Note:** The first time you *push* a feature branch you will probably need to
use `--set-upstream origin` to link to your remote fork:

```bash
  git push --set-upstream origin <your-branch-name>
```

### Open a Pull Request

When you feel that work on your new feature is complete, you should create a
*Pull Request*. This will propose your work to be merged into the main
AgriFoodPy repository.

  1. Go to [AgriFoodPy Pull Requests](https://github.com/FixOurFood/AgriFoodPy/pulls)
  2. Click the green **New pull request** button
  3. Click **compare across forks**
  4. Confirm that the base fork is ``FixOurFood/AgriFoodPy`` and the basebranch is ``main``
  5. Confirm the head fork is ``<your-account>/AgriFoodPy`` and the compare branch is ``<your-branch-name>``
  6. Give your pull request a title and fill out the the template for the description
  7. Click the green **Create pull request** button

### Status checks

A series of automated checks will be run on your pull request, some of which will
be required to pass before it can be merged into the main codebase:

  - ``Tests`` (Required) runs the `unit tests`
  <!-- - ``Code Style`` (Required) runs `flake8 <https://flake8.pycqa.org/en/latest/>`__ to check that your code conforms to the `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guidelines. Click "Details" to view any errors. -->
  <!-- - ``codecov`` reports the test coverage for your pull request; you should aim for `codecov/patch — 100.00%`. Click "Details" to view coverage data. -->
  - ``docs`` (Required) builds the `docstrings` on [readthedocs](https://readthedocs.org/).

### Updating your branch

As you work on your feature, new commits might be made to the ``agrifoodpy`` main
branch. You will need to update your branch with these new commits before your
pull request can be accepted. You can achieve this in a few different ways:

  - If your pull request has no conflicts, click **Update branch**
  - If your pull request has conflicts, click **Resolve conflicts**,
    manually resolve the conflicts and click **Mark as resolved**
  - *merge* the ``agrifoodpy`` main branch from the command line:

```bash
        git fetch AgriFoodPyproject
        git merge AgriFoodPyproject/main
```
  - *rebase* your feature branch onto the ``agrifoodpy`` main branch from the command line:

```bash
        git fetch AgriFoodPyproject
        git rebase AgriFoodPyproject/main
```

**Warning**: It is bad practice to *rebase* commits that have already been pushed
to a remote such as your fork. Rebasing creates new copies of your commits that
can cause the local and remote branches to diverge. ``git push --force`` will
**overwrite** the remote branch with your newly rebased local branch. This is
strongly discouraged, particularly when working on a shared branch where you
could erase a collaborators commits.

For more information about resolving conflicts see the GitHub guides:
  - [Resolving a merge conflict on GitHub](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/resolving-a-merge-conflict-on-github)
  - [Resolving a merge conflict using the command line](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/resolving-a-merge-conflict-using-the-command-line)
  - [About Git rebase](https://help.github.com/en/github/using-git/about-git-rebase)

## More Information

More information regarding the usage of GitHub can be found in the
[GitHub Guides](https://guides.github.com).
