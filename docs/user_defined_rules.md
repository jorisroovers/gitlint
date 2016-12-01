# User Defined Rules
Gitlint versions 0.8.0 and above support the concept of User Defined rules: the ability for you
to write your own custom rules that are executed when gitlint is.

This can be done using the ```extra-path``` general option, which can be set using the ```--extra-path```
commandline flag, by adding it under the ```[general]``` section in your ```.gitlint``` file or using
one of the other ways to configure gitlint.  For more details, please refer to the
[Configuration](configuration.md) page.

If you want to check whether your rules are discovered, you can use the ```--debug``` flag:

```bash
$ gitlint --debug
TODO: CONTINUE
```


## TODO:
- Document extra_config parameter in the configuration section

## Rule requirements

As long as you stick with simple scenarios that are similar to the sample User Defined rules (see the ```examples``` directory), gitlint
should be able to discover and execute your custom rules. If you want to do something more exotic however, you might run into some issues.

While the [rule finding source-code](https://github.com/jorisroovers/gitlint/blob/master/gitlint/user_rules.py) is the
ultimate source of truth, here are some of the requirements that gitlint enforces:

### Extra path requirements ###
- The ```extra-path``` option must point to a **directory**, not a file
- The ```extra-path``` directory does **not** need to be a proper python package, i.e. it doesn't require an ```__init__.py``` file.
- Python files containing user rules must have a ```.py``` extension. Files with a different extension will be ignored.
- The ```extra-path``` will be searched non-recursively, i.e. all rule classes must be present at the top level ```extra-path``` directory.
- User rule classes must be defined in the modules that are part of ```extra-path```, rules that are imported from outside the ```extra-path``` will be ignored.

### Rule class requirements ###

- Rules *must* extend from  ```LineRule``` or ```CommitRule```
- Rule classes *must* have ```id``` and ```name``` string attributes. The ```options_spec``` is optional, but if set, it *must* be a list.
- Rule classes *must* have a ```validate``` method. In case of a ```CommitRule```, ```validate```  *must* take a single ```commit``` parameter.
  In case of ```LineRule```, ```validate``` must take ```line``` and ```commit``` as first and second parameters.
- User Rule id's *cannot* be of the form ```R[0-9]+```, ```T[0-9]+```, ```B[0-9]+``` or ```M[0-9]+``` as these rule ids are reserved for gitlint itself.
- Rule *should* have a unique id as only one rule can exist with a given id. While gitlint does not enforce this, the rule that will
  actually be chosen will be system specific.
