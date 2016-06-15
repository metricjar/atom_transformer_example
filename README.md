Atom Transformer Example (for tests)
====

Here you can see an example of how we will transform an event.

``` ./events.txt```: will hold all the events that are needed to be transformed.

```./atom_transformer_dev/base.py```: will hold mock enrichment's function that we use

``` ./transformer_example.py ```: inherits from base class and will be the actual transformer




### How to use:
- Clone this repository

- Edit transformer_example.py after the ```# TODO```:
 
- Replace the demo events in events.txt with real life examples of your use case.

- Run:
```
$ python transformer_example.py events.txt
```

- The result of our transformer will be printed on the screen


### version:
- This example is written in python 2.7, if there is something that is not supported for your needs, please open an issue and we will try to solve it.
