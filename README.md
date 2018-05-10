# GraphQL wrap

Test GraphQL wrapping around an (old) version of the genomics APIs, just individuals and variants for now.
Everything is implemented in the simplest (==dumbest) way possible, but improving the performance is easy
with dataloaders.

```
pip install -r requirements.txt
python graphqlwrap.py
```

## Examples

Some demo queries:

Getting variants linked to an individual
```
{
  oneindividual(id:"WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDI1NSJd") {
    id,
    name,
    variants {
      names
    }
  }
}
```

Getting individual fields linked to a variant:

```
{
  variants(start:"1", end:"100000") {
    names,
    calls {
        individual {
            name,
            description
      }
    }
  }
}
```
