from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"GEMINI_API_KEY is found")
else:
    print("GEMINI_API_KEY not found in environment variables.")


###########################################################################################
def ask_and_record(
        prompt, 
        model = "gemini-3-flash-preview", filename = "gemini_history.txt"): 
  
    print(f"Sending question: {prompt}...")
    
    response = client.models.generate_content(
        model= model, 
        contents=prompt
    )
    
    answer = response.text
    # Record the response
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"Q: {prompt}\n")
        f.write(f"A: {answer}\n")
        f.write("-" * 30 + "\n")
    
    return answer

link = "https://www.sec.gov/ix?doc=/Archives/edgar/data/0001257640/000110465926025219/kro-20251231x10k.htm"
question = f"""
Look at this link, show me revenue segments and its mix, and its top competitors in each segment. 
{link}
"""

# Example usage
result = ask_and_record(question)
print(f"\nGemini's Response:\n{result}")


###########################################################################################

from google import genai
from pydantic import BaseModel, Field
from typing import List, Optional
import os

class Ingredient(BaseModel):
    name: str = Field(description="Name of the ingredient.")
    quantity: str = Field(description="Quantity of the ingredient, including units.")

class Recipe(BaseModel):
    recipe_name: str = Field(description="The name of the recipe.")
    prep_time_minutes: Optional[int] = Field(description="Optional time in minutes to prepare the recipe.")
    ingredients: List[Ingredient]
    instructions: List[str]

client = genai.Client()

prompt = """
Please extract the recipe from the following text.
The user wants to make delicious chocolate chip cookies.
They need 2 and 1/4 cups of all-purpose flour, 1 teaspoon of baking soda,
1 teaspoon of salt, 1 cup of unsalted butter (softened), 3/4 cup of granulated sugar,
3/4 cup of packed brown sugar, 1 teaspoon of vanilla extract, and 2 large eggs.
For the best part, they'll need 2 cups of semisweet chocolate chips.
First, preheat the oven to 375°F (190°C). Then, in a small bowl, whisk together the flour,
baking soda, and salt. In a large bowl, cream together the butter, granulated sugar, and brown sugar
until light and fluffy. Beat in the vanilla and eggs, one at a time. Gradually beat in the dry
ingredients until just combined. Finally, stir in the chocolate chips. Drop by rounded tablespoons
onto ungreased baking sheets and bake for 9 to 11 minutes.
"""

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt,
    config={
        "response_mime_type": "application/json",
        "response_json_schema": Recipe.model_json_schema(),
    },
)

recipe = Recipe.model_validate_json(response.text)
print(recipe)