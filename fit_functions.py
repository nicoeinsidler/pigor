import numpy as np

fit_function_list = dict()

def register_fit_function(func, bounds=(-np.inf, np.inf)):
    """This decorator registers a new fit function and writes an entry to fit_function_list."""
    global fit_function_list
    fit_function_list[func.__name__] = (func, bounds)
    return func

@register_fit_function
def gauss(x, a, x0, sigma, export=False):
    """Gaussian function, used for fitting data.

    :param x: parameter
    :param a: amplitude
    :param x0: maximum
    :param sigma: width
    :param export: enable text output of function

    """
    if export == 'Mathematica':
        return f'{a} * Exp[-({x}-{x0})^2 / (2*{sigma}^2)]'
    else:
        return a*np.exp(-(x-x0)**2/(2*sigma**2))

@register_fit_function
def sine_lin(x, a, omega, phase, c, b, export=False):
    """Sine function with linear term added for fitting data.

    :param x: parameter
    :param a: amplitude
    :param omega: frequency
    :param phase: phase
    :param c: offset
    :param b: slope
    :param export: enable text output of function

    """
    if export == 'Mathematica':
        return f'{a} * Sin[{x}*{omega} + {phase}] + {b}*{x} + {c}'
    else:
        return a*np.sin(x*omega + phase) + b*x + c

@register_fit_function
def poly5(x, a5, a4, a3, a2, a1, a0, export=False):
    """Polynom 5th degree for fitting.

    :param x: parameter
    :param a5: coeff
    :param a4: coeff
    :param a3: coeff
    :param a2: coeff
    :param a1: coeff
    :param a0: coeff
    :param export: enable text output of function

    :returns: function -- polynomial 5th degree
    """
    if export == 'Mathematica':
        return f'((((({a5}*{x} + {a4})*{x} + {a3})*{x} + {a2})*{x} + {a1})*{x} + {a0})'
    else:
        return (((((a5*x + a4)*x + a3)*x + a2)*x + a1)*x + a0)


def poly(x, a, export=False):
    """Polynom nth degree for fitting.
    
    :param x: parameter
    :type x: int, float
    :param a: list of coefficients [a_N,a_N-1, ..., a_1, a_0]
    :type a: list
    :param export: enable text output of function, defaults to False
    :type export: bool or string, optional
    :return: returns the polynomial
    :rtype: str, int, float


    >>> poly(3.4543, [5,4,3,2,1], export='Mathematica')
    '5*3.4543^5 + 4*3.4543^4 + 3*3.4543^3 + 2*3.4543^2 + 1*3.4543^1'

    >>> poly(3.4543, [5,4,3,2,1])
    920.4602110784704
    """
    if export == 'Mathematica':
        return ' + '.join([f'{a[i]}*{x}^{len(a)-i}' for i in range(len(a))])
    else:
        return poly(x, a[0:-1])*x + a[-1] if len(a) > 1 else a[0]


@register_fit_function
def sine(x, a, omega, phase, c, export=False):
    """Sine function for fitting data.

    :param x: parameter
    :param a: amplitude
    :param omega: frequency
    :param phase: phase
    :param c: offset
    :param export: enable text output of function

    """
    if export == 'Mathematica':
        return f'{a}*Sin[{x}*{omega} + {phase}] + {c}'
    else:
        return a*np.sin(x*omega + phase) + c