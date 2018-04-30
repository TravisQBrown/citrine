# -*- coding: utf-8 -*-

## Flask is a lightweight Python library for with RESTful request dispatching
from flask import Flask,redirect, request

## Pyparsing is a library for defining context-free grammars.
## Used here to assist in parsing infix mathematics operations
import pyparsing as pyp

app = Flask(__name__)

# module scope variable.  Used to construct result
template = '{ "unit_name": "<UN>", "multiplication_factor": <MF> }'

# HashMap to map provided units into si units.  Based upon provided table
unit_conversion_map = {
    "minute": {"si_symbol": "s", "si_unit": 60},
    "min": {"si_symbol": "s", "si_unit": 60},
    "hour": {"si_symbol": "s", "si_unit": 3600},
    "h": {"si_symbol": "s", "si_unit": 3600},
    "day": {"si_symbol": "s", "si_unit": 86400},
    "d": {"si_symbol": "s", "si_unit": 86400},
    "degree": {"si_symbol": "rad", "si_unit": 0.01745329251994},
    "°": {"si_symbol": "rad", "si_unit": 0.01745329251994},
    "arcminute": {"si_symbol": "rad", "si_unit": 0.00029088820866},
    "'": {"si_symbol": "rad", "si_unit": 0.00029088820866},
    "arcsecond": {"si_symbol": "rad", "si_unit": 0.00000484813681},
    '"': {"si_symbol": "rad", "si_unit": 0.00000484813681},
    "hectare": {"si_symbol": "m^2", "si_unit": 10000},
    "ha": {"si_symbol": "m^2", "si_unit": 10000},
    "litre": {"si_symbol": "m^3", "si_unit": .001},
    "L": {"si_symbol": "m^3", "si_unit": .001},
    "tonne": {"si_symbol": "kg", "si_unit": 1000},
    "t": {"si_symbol": "kg", "si_unit": 1000}
}

# Route default route to citrine website.
@app.route('/')
def citrine_root():
    return redirect('https://citrine.io')

# Convert provided units into si units, return JSON object in form of
# module variable 'template'
@app.route('/units/si')
def convert_units():
    units = request.args.get('units')

    # If units query param not provided, return empty si equivalent and identity for factor
    if units is None:
        return construct_result('',1)

    try:
        param_list = parse_params(units)
        #Transform the provided parameters into two lists
        si_param_list, si_factor_list = transform_to_si( param_list )
        si_param_str = infix_string_from_list( si_param_list)
        si_mult_factor = derive_multiplication_factor(si_factor_list)
        return construct_result( si_param_str, si_mult_factor)
    except Exception as e :
        return construct_result( str(e), 1 )


## Utility to construct JSON result of endpoint /units/si
def construct_result( si_param_str, si_mult_factor):
    ret_val = template
    ret_val = template.replace('<UN>', si_param_str)
    ret_val = ret_val.replace('<MF>', str(si_mult_factor))
    return ret_val


## Transform the provided list into a string that adheres to infix notation
def infix_string_from_list( infix_list ):
    open_paren = str(infix_list).replace('[', '(')
    close_paren = str(open_paren).replace(']', ')')
    no_commas = str(close_paren).replace(',', '')
    no_oper_apos = str(no_commas).replace("'", "")
    return no_oper_apos[1:-1] #Remove opening and closing parens from original list



## Derive the multiplication factor
def derive_multiplication_factor( factor_list ):
    infix_str = infix_string_from_list(factor_list)
    mult_factor = eval(infix_str)
    return mult_factor

## Transform a string formula of non-si units formatted in infix notation into
## a hierarchical list of si units.  Each list represents an infix expression
def transform_to_si( param_list ):
    symbol_list = []
    factor_list = []
    operators = set('*/+-')

    for item in param_list:

        # A list is an expression.  Examples: (a * b) or ((a * (b/c))
        if type(item) is list:
            sub_symbol_list, sub_factor_list = transform_to_si(item)
            symbol_list.append(sub_symbol_list)
            factor_list.append(sub_factor_list)

        # Otherwise, item is a term, factor or operator
        else:
            symbol = item
            factor = item

            # If not an operator, get si values that map the term or factor
            if not any(( o in operators) for o in item):

                # Throw exception if unit does not have si equivalent
                if item not in unit_conversion_map:
                    raise Exception(item + ' does not have an si equivalent')

                append_items =unit_conversion_map.get(item)
                symbol = append_items.get("si_symbol")
                factor = append_items.get("si_unit")

            symbol_list.append(symbol)
            factor_list.append(factor)

    return symbol_list, factor_list

# Use pyparsing module to arse query string value into list.  Lists easily
# accommodate infix subexpressions (i.e. (a - (b / c)) ).
def parse_params( param_str ):
    integer = pyp.Word(pyp.nums)
    float = pyp.Word(pyp.nums+'.')
    operand = pyp.Word(pyp.alphas+'°\'\"')
    try:
        expr = pyp.infixNotation(operand,
            [
                (pyp.oneOf('* /'), 2, pyp.opAssoc.LEFT),
                (pyp.oneOf('+ -'), 2, pyp.opAssoc.LEFT),
             ])

        expr_parsed = expr.parseString(param_str)
        result = expr_parsed.asList()
    except Exception as e:
        raise Exception(param_str+ ' is an invalid expression')

    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0')
