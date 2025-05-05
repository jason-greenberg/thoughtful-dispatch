# Thoughtful-dispatch

- **Github repository**: <https://github.com/jason-greenberg/thoughtful-dispatch/>

## Setup

Install the environment and the pre-commit hooks with

```bash
make install
```

## Usage

The core logic for sorting packages based on dimensions and mass is in `thoughtful_dispatch/sorter.py`.

To run the example cases defined within the script, execute:

```bash
make run
```

This will print the results for various standard, special, rejected, edge-case, and invalid inputs using the examples defined in the `if __name__ == "__main__":` block of `sorter.py`.

## Tests

To run tests on `thoughtful_dispatch/sorter.py`:

```bash
make test
```
