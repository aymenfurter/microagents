# Microagents: Modular Agents Capable of Self-Editing and Enhancing Their Prompts and Python code

![Self-Composing Agents](static/output.gif?raw=true)

## Overview
This experiment explores self-evolving agents that automatically generate and improve themselves to answer a variety of questions. No specific agent design or prompting is required from the user. Simply pose a question, and the system initiates and evolves agents tailored to provide answers. Microagents are designed for reuse and can learn from past mistakes to enhance their future performance.

## Generated Prompts from above Demo
```
Prompt for CalculateAddition:
You are an adept arithmetic solver with focus on performing addition. Utilize this Python function to calculate the sum of two numbers:

``python
def calculate_addition(num1, num2):
    return num1 + num2

# Example usage:
print(calculate_addition(5, 9))
``

Prompt for GetPopulationOfCountry:
You are a skilled data extractor specializing in population statistics. Retrieve the population of a given country using the provided Python code:

``python
import requests

def get_population(country):
    url = f"https://restcountries.com/v3.1/name/{country}"
    response = requests.get(url).json()
    population = response[0]['population']
    print(f"The population of {country} is {population}.")

# Example usage:
get_population("CountryName")
``

```

## Current Challenges and Potential Improvements

1. **Path Optimization**: The system sometimes fails to effectively discard non-functional evolutionary paths. Improving this mechanism is essential for more reliable results.

2. **Performance and Parallelization**: Currently, parallel processing is not implemented. Enabling the testing of multiple prompt evolutions simultaneously could significantly enhance performance.

3. **Strategy for Prompt Evolution**: The approach to prompt evolution is quite basic at the moment. Developing a method to quantify the success ratio would refine this strategy. 

4. **Persistent Agent Prompts**: There is significant potential in integrating persistent agent prompts with vector databases. Additionally, sharing successful agents across various runtime environments could improve overall efficiency.

5. **Hierarchical Agent Structure**: Most requests are presently processed directly by an agent designated by the bootstrap agent. Implementing a more intricate hierarchical structure for managing requests could lead to major improvements.
