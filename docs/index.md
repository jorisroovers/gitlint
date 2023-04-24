# Introduction
Gitlint is a git commit message linter written in python: it checks your commit messages for style.

Great for use as a [commit-msg git hook](#using-gitlint-as-a-commit-msg-hook) or as part of your gating script in a
[CI pipeline (e.g. Jenkins)](index.md#using-gitlint-in-a-ci-environment).

<!-- <script type="text/javascript" src="https://asciinema.org/a/30477.js" id="asciicast-30477" async></script>  -->

<div class="termynal" data-termynal data-ty-typeDelay="25" data-ty-startDelay="600"  data-ty-lineDelay="500">
    <span data-ty="input">pip install gitlint</span>
    <span data-ty="progress"></span>
    <span data-ty>Successfully installed gitlint-core, gitlint</span>
    <span data-ty></span>
    <span data-ty="comment"># Add a bad commit message</span>
    <span data-ty="input">git commit --allow-empty  -m " WIP: My bad commit title." -m "who &emsp; cares "</span>
    <span>[main a9f9368]  WIP: My bad commit title.</span>
    <span data-ty></span>
    <span data-ty="comment"># Run gitlint!</span>
    <span data-ty="input">gitlint</span>e
    <span data-ty>1: T3 Title has trailing punctuation (.): " WIP: My bad commit title."<br />
                  1: T5 Title contains the word 'WIP' (case-insensitive): " WIP: My bad commit title."<br />
                  1: T6 Title has leading whitespace: " WIP: My bad commit title."<br />
                  3: B2 Line has trailing whitespace: "who &emsp; cares "<br />
                  3: B3 Line contains hard tab characters (\t): "who &emsp; cares "<br />
                  3: B5 Body message is too short (10&lt;20): "who &emsp; cares "
    </span>
    <span data-ty data-ty-delay="2000"></span>
    <span data-ty></span>
    <span data-ty="comment"># Gitlint is perfect for use in your CI pipeline.</span>
    <span data-ty="comment"># Also available as a commit-msg hook or via pre-commit.</span>
</div>

!!! note
    Also, gitlint is not the only git commit message linter out there, if you are looking for an alternative written in a different language,
    have a look at [fit-commit](https://github.com/m1foley/fit-commit) (Ruby),
    [node-commit-msg](https://github.com/clns/node-commit-msg) (Node.js) or [commitlint](http://marionebl.github.io/commitlint) (Node.js).


## Features
 - **Commit message hook**: [Auto-trigger validations against new commit message right when you're committing](#using-gitlint-as-a-commit-msg-hook). Also [works with pre-commit](#using-gitlint-through-pre-commit).
 - **Easily integrated**: Gitlint is designed to work [with your own scripts or CI system](#using-gitlint-in-a-ci-environment).
 - **Sane defaults:** Many of gitlint's validations are based on
[well-known](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html),
[community](https://addamhardy.com/2013-06-05-good-commit-messages-and-enforcing-them-with-git-hooks),
[standards](http://chris.beams.io/posts/git-commit/), others are based on checks that we've found
useful throughout the years.
 - **Easily configurable:** Gitlint has sane defaults, but [you can also easily customize it to your own liking](configuration.md).
 - **Community contributed rules**: Conventions that are common but not universal [can be selectively enabled](contrib_rules.md).
 - **User-defined rules:** Want to do more then what gitlint offers out of the box? Write your own [user defined rules](user_defined_rules.md).
 - **Full unicode support:** Lint your Russian, Chinese or Emoji commit messages with ease!
 - **Production-ready:** Gitlint checks a lot of the boxes you're looking for: actively maintained, high unit test coverage, integration tests,
   python code standards ([black](https://github.com/psf/black), [ruff](https://github.com/charliermarsh/ruff)),
   good documentation, widely used, proven track record.
