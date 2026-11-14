# tennispack

A Python package for retrieving, cleaning, and visualizing professional tennis players' career match data.

This package was developed for UC Berkeley's STAT 159 Homework 3, building on the data collection and visualization work from HW1 and HW2.

## Overview

`tennispack` allows users to retrieve tennis match data from Tennis Abstract and generate scatter plots comparing a player's age with the age difference between the player and their opponents.

The package provides two main functions:

- `get_player_data(player_name)`: Retrieves and processes a player's career match data into a pandas DataFrame.
- `plot_player_matches(df)`: Generates a scatter plot showing player age on the x-axis and the difference between player and opponent ages on the y-axis, with matches colored by win/loss status.

The package supports both men's and women's tennis data and handles differences in how opponent ages are recorded.

## Installation

The package can be installed directly from GitHub using pip:

```bash
pip install git+https://github.com/UCB-stat159-f26/hw03-2-tiffanyyu91.git
```

Dependencies include:

- pandas
- requests
- matplotlib

## Usage

Import the two main functions:

```python
from tennispack import get_player_data, plot_player_matches
```

### Retrieving Player Data

Retrieve Serena Williams's career match data:

```python
serena = get_player_data("Serena Williams")
print(serena.head())
```

The function returns a DataFrame containing match dates, results, opponent names, opponent ages, player ages, and age differences.

The same function can be used for other players:

```python
rafa = get_player_data("Rafael Nadal")
iga = get_player_data("Iga Swiatek")
```

Player names can be provided with different capitalizations and spacing, subject to Tennis Abstract's player naming conventions.

### Creating Visualizations

Generate a scatter plot for Serena Williams:

```python
plot_player_matches(serena)
```

Or for Rafael Nadal:

```python
plot_player_matches(rafa)
```

The visualization displays:

- **X-axis:** Player's age at the time of the match
- **Y-axis:** Player's age minus opponent's age
- **Color:** Win or loss

A horizontal reference line at zero indicates when the player and opponent were the same age.

### Invalid Inputs

If the requested player's data cannot be found, the function raises a meaningful error.

For example:

```python
get_player_data("Tiffany Yu")
```

## Data Sources and Processing

Career match data is retrieved from [Tennis Abstract](https://www.tennisabstract.com/).

The package extracts match records from JavaScript files and converts them into pandas DataFrames.

Because opponent information is stored differently across player datasets, the package handles both birth dates and numerical ages. When opponent birth dates are provided, the package calculates their ages at the time of each match.

Player birth dates are retrieved using Tennis Abstract player profiles and an external [WTA player dataset](https://github.com/ivanxieau/WTA_TennisAbstract).

Age differences are calculated as:

**Age Difference = Player Age − Opponent Age**

The package requires an internet connection to retrieve player data. Availability depends on the external data sources, and some players or records may be unavailable.

## Testing

Automated tests are included in the `tests/` directory.

The tests cover:

- Player name normalization
- Invalid name inputs
- Parsing JavaScript match records
- Processing female player match data
- Processing male player match data
- Calculating player and opponent ages

Tests use simulated match records instead of requesting data from live Tennis Abstract servers.

To run the tests, navigate to the project directory and execute:

```bash
python -m pytest tests/ -v
```

## Personal Reflections

This assignment was really interesting. Throughout my time at Berkeley, I have imported packages hundreds of time but never examined what a package was made of. With this homework, I learned how to turn code into a reusable python package. I also learned how to separate scripts into organized code functions and edit code so that each function was not too long. This was to ensure readability and generalizable code so that someone else could install and use it. 

One challenge was working with both men's and women's data. There were inconsistencies in how the age data was presented either with a birth date or an actual age. Several times, my code would pull a women's birthday from the men's data set resulting in a crazy age and age difference with their opponent. I had to debug the code to retrieve the correct player information with the correct gender data set. Debugging these problems reinforced the importance of checking intermediate outputs rather than assuming that successfully running code means the results are correct.

I also learned more about Python package structure. I learned more about `__init__.py`, `pyproject.toml`, and separate modules for data processing and visualization. Writing automated tests helped me understand how to verify individual functions without relying on external websites.

Overall, this assignment gave me more experience with modular programming, debugging, automated testing, and reproducibility. It also helped me see how organizing code into a package makes an analysis easier to reuse and maintain.
