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

and you'll get something like:
```
{
  "data": {
    "oneindividual": {
      "id": "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDI1NSJd",
      "name": "HG00255",
      "variants": [
        {
          "names": [
            "rs376342519"
          ]
        },
        {
          "names": [
            "rs531730856"
          ]
        },
        {
          "names": [
            "rs546169444"
...
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

and you'll get:
```
{
  "data": {
    "variants": [
      {
        "names": [
          "rs367896724"
        ],
        "calls": [
          {
            "individual": {
              "name": "HG00530",
              "description": "CHS"
            }
          },
          {
            "individual": {
              "name": "HG00306",
              "description": "FIN"
            }
          },
          {
            "individual": {
              "name": "HG00308",
              "description": "FIN"
            }
          },
          {
            "individual": {
              "name": "HG00155",
              "description": "GBR"
            }
          }
        ]
      },
...
```
