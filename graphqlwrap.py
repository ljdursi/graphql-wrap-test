"""
GraphQL example wrapping ga4gh.ccm.sickkids.ca/ga4gh
"""
import os
import json
import requests
from collections import namedtuple as nt
from graphene import ObjectType, List, ID, String, Boolean, Float
from graphene import Schema, Field
from flask import Flask
from flask_graphql import GraphQLView


def json2obj(data):
    """ Convert a json document into a python object """
    return json.loads(data,
                      object_hook=lambda d: nt('X', d.keys())(*d.values()))


_CALLSETIDS = ["WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMTA2MCJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDk3OCJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDk1NiJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDg0NCJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDUzMCJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDM3NiJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDYxMyJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDI1NSJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDMwNiJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDMwOCJd",   # noqa: E501
               "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIiwiSEcwMDE1NSJd"]   # noqa: E501

_NAMES = ["HG01060", "HG00978", "HG00956", "HG00844", "HG00530", "HG00376",
          "HG00613", "HG00255", "HG00306", "HG00308", "HG00155"]

_IDS = ["WyIxa2dlbm9tZXMiLCJpIiwiSEcwMTA2MCJd", "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDk3OCJd",  # noqa: E501
        "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDk1NiJd", "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDg0NCJd",  # noqa: E501
        "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDUzMCJd", "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDM3NiJd",  # noqa: E501
        "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDYxMyJd", "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDI1NSJd",  # noqa: E501
        "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDMwNiJd", "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDMwOCJd",  # noqa: E501
        "WyIxa2dlbm9tZXMiLCJpIiwiSEcwMDE1NSJd"]


class Individual(ObjectType):
    id = ID()
    name = String()
    datasetId = String()
    description = String()
    variants = List(lambda: Variant)

    def resolve_variants(self, info, **kwargs):
        variants = get_variants(info, **kwargs)
        myvariants = []
        for var in variants:
            for call in var['calls']:
                if call['callSetName'] == self.name:
                    myvariants.append(var)
        return json2obj(json.dumps(myvariants))


class Call(ObjectType):
    callSetName = String()
    genotype = List(Float)
    callSetId = ID()
    phaseSet = Boolean()
    individual = Field(Individual)

    def resolve_individual(self, info, **kwargs):
        BASE_URL = "http://ga4gh.ccm.sickkids.ca/ga4gh"
        individuals_endpoint = BASE_URL + "/individuals/search"
        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json'}
        data = {"dataset_id": "WyIxa2dlbm9tZXMiXQ"}

        resp = requests.post(individuals_endpoint, headers=headers, json=data)
        individuals = resp.json()['individuals']
        individual = [ind for ind in individuals
                      if ind['name'] == self.callSetName]
        individual = individual[0]
        return json2obj(json.dumps(individual))


class Attribute(ObjectType):
    name = String()
    value = String()


def filtercalls(variant):
    goodcalls = [c for c in variant['calls'] if sum(c['genotype']) > 0]
    variant['calls'] = goodcalls
    return variant


def filtervariants(variants):
    return [v for v in variants if len(v['calls']) > 0]


def attr_val(values):
    return values['values'][0].values()[0]


def transform_attributes(variant):
    attrs = variant['attributes']['attr']
    transformed = [{"name": key, "value": str(attr_val(attrs[key]))}
                   for key in attrs.keys()]
    variant['attributes'] = transformed
    return variant


def variants_of_interest(variants):
    vars_with_good_calls = [filtercalls(v) for v in variants]
    filtered = filtervariants(vars_with_good_calls)
    attrsfixed = [transform_attributes(v) for v in filtered]
    return attrsfixed


def get_variants(info, **kwargs):
    _JSON = "application/json"
    _BASEURL = "https://ga4gh.ccm.sickkids.ca/ga4gh/"
    _VARIANTSETID = "WyIxa2dlbm9tZXMiLCJ2cyIsInBoYXNlMy1yZWxlYXNlIl0"

    reference_name = "1"
    sstart = 1
    send = 100000

    if 'reference_name' in kwargs:
        reference_name = kwargs['reference_name']
    if 'start' in kwargs:
        sstart = kwargs['start']
    if 'end' in kwargs:
        send = kwargs['end']

    headers = {'Accept': _JSON, 'Content-type': _JSON}
    variants_endpoint = _BASEURL + "/variants/search"
    data = {"variant_set_id": _VARIANTSETID,
            "reference_name": reference_name,
            "start": sstart,
            "end": send,
            "call_set_ids": _CALLSETIDS}

    resp = requests.post(variants_endpoint, headers=headers, json=data)
    all_variants = resp.json()['variants']
    good_variants = variants_of_interest(all_variants)
    return good_variants


class Variant(ObjectType):
    id = ID()
    variantSetId = ID()
    start = String()
    end = String()
    names = List(String)
    filtersApplied = Boolean()
    filtersPassed = Boolean()
    referenceName = String()
    referenceBases = String()
    alternateBases = List(String)
    attributes = List(Attribute)
    calls = List(Call)


class Query(ObjectType):
    individuals = List(Individual)
    oneindividual = Field(Individual, id=String())

    variants = List(Variant, start=String(), end=String())

    def resolve_individuals(self, info):
        BASE_URL = "http://ga4gh.ccm.sickkids.ca/ga4gh"
        individuals_endpoint = BASE_URL + "/individuals/search"
        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json'}
        data = {"dataset_id": "WyIxa2dlbm9tZXMiXQ"}

        resp = requests.post(individuals_endpoint, headers=headers, json=data)
        individuals = resp.json()['individuals']
        individuals = [ind for ind in individuals if ind['id'] in _IDS]  # noqa: E501
        return json2obj(json.dumps(individuals))

    def resolve_oneindividual(self, info, **kwargs):
        BASE_URL = "http://ga4gh.ccm.sickkids.ca/ga4gh"
        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json'}
        gid = kwargs['id']
        individual_endpoint = BASE_URL + "/individuals/" + gid
        resp = requests.get(individual_endpoint, headers=headers)
        individual = resp.json()
        return json2obj(json.dumps(individual))

    def resolve_variants(self, info, **kwargs):
        variants = get_variants(info, **kwargs)
        return json2obj(json.dumps(variants))


def main():
    view_func = GraphQLView.as_view(
        'graphql', schema=Schema(query=Query), graphiql=True)

    app = Flask(__name__)
    app.add_url_rule('/graphql', view_func=view_func)

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))


if __name__ == "__main__":
    main()
