# Designing a Unified Food Nutrition Lookup API (FastAPI Aggregator)

Objective: Build a production-grade FastAPI service that aggregates three data sources – USDA FoodData Central (FDC), Open Food Facts (OFF), and GS1 Global Product Classification (GPC) – into one canonical “food intelligence” API. The service will asynchronously fetch data from all sources by GTIN/UPC barcode (the primary key for lookup), reconcile the disparate data into a single Pydantic model, and return a unified JSON response. The focus here is on the data model, data mapping, and conflict-resolution logic first, followed by the API implementation and deployment considerations.

## Objectives

### Unified Key: Barcode-Driven Lookup

All product queries use the GTIN/UPC barcode as the unique identifier – no free-text search. This ensures unambiguous results and aligns with industry practice of using barcodes to identify products. If a GTIN isn’t found in the primary source (USDA), the API automatically falls back to secondary sources so that coverage remains broad.

### Standardized Nutrition per 100g

Nutrient values are normalized per 100 g (or 100 mL) for comparability across products and serving sizes. This mirrors Open Food Facts’ approach of providing fields like fat_100g or protein_100g in its API. The original serving size and its nutrition data can be retained as metadata, but the canonical model’s primary values are all on a 100g basis for consistency.

### Ranked Sources & Conflict Resolution

The system follows a “ranked truth” model: USDA FoodData Central is treated as the most reliable source for nutritional data, Open Food Facts provides breadth (many products & user-contributed info) and is used as fallback plus a source of images/ingredients, and GS1 GPC supplies the official product category taxonomy. When data overlaps, USDA values override others (e.g. if USDA reports 100 kcal and OFF reports 110 kcal, the unified result uses 100 kcal). This ensures scientifically validated nutrition info is prioritized, while still leveraging OFF for missing data and product details.

### Fast & Resilient API Calls

To achieve low latency (<500 ms target response time), the API calls all three sources in parallel using asynchronous I/O. The design includes graceful degradation: if one source is slow or unavailable (e.g. USDA API downtime), the service returns what data is available from the others, along with metadata indicating which sources contributed. This ensures the API responds quickly and never fails entirely due to a single upstream dependency.

## High-Level Architecture

“Unified Food Intelligence” API: The FastAPI service acts as an aggregation gateway to the three data providers. On each lookup request, it will concurrently retrieve:

- USDA FoodData Central (FDC) – Provides lab-quality nutrient data for foods (especially branded products and foundational foods). This is the gold standard for nutritional values and will be the authoritative source for calories, macros, vitamins, etc. [github.com]
- Open Food Facts (OFF) – A crowdsourced global database of over 3 million food products. OFF contributes broad coverage (many international products that may not be in USDA) and additional fields like product names in various locales, brands, ingredients list, allergen info, and product images. OFF also has community-entered nutrition facts which we use only if USDA data is unavailable for a given item. [github.com]
- GS1 GPC (Global Product Classification) – An industry-standard taxonomy that classifies products into a hierarchy (Segment – Family – Class – Brick). GS1 GPC doesn’t provide nutrition, but gives each product a category code and description, ensuring our API can output a standardized category hierarchy (e.g. “Beverages > Carbonated Drinks > Soft Drinks > Cola”) for each item. [github.com]

Workflow: A single GET request triggers three asynchronous queries (one to each source). When all return (or time out), a Data Orchestrator layer merges the results into one canonical representation. The merger applies our source-priority rules (USDA first for nutrients, OFF next, GS1 for taxonomy) and formats the data into a cohesive JSON object. This aggregated result is then returned to the client. Thanks to FastAPI and asynchronous i/o, this happens quickly even though multiple external APIs are involved – network calls are done in parallel, not sequentially. [github.com]

Resilience: The service is designed so that a failure in any single upstream will not break the entire response. For example, if the USDA API call errors out or is slow, the Open Food Facts data (which might include at least an approximate nutrition from the package) is still returned, along with an indication that the USDA source is missing. The client can see in the data_sources field which sources were used. Similarly, if OFF doesn’t have the product, but USDA does (common for U.S. products with an official dataset), you still get core nutrition from USDA. This graceful degradation ensures high availability of the API.


## Canonical Data Model and Schema Reconciliation

At the heart of the design is a canonical data model that harmonizes fields from all sources. We define a Pydantic model CanonicalProduct that acts as the single source of truth in the API, abstracting away the differences in upstream schemas. This model is what the FastAPI endpoint returns, and it includes all relevant information about a food product across nutrition, classification, and metadata. Below is the structure of the canonical model with its key fields:

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

class NutrientValue(BaseModel):
    value: float
    unit: str = "g"           # default unit (grams for most macros)

class CanonicalProduct(BaseModel):
    gtin: str                 # The product barcode used as key
    product_name: str         # Unified product name (prefers official naming)
    brand: Optional[str] = None
    category_hierarchy: List[str] = Field(
        default=[], description="GS1 category path: Segment/Family/Class/Brick"
    )
    # Normalized nutrition facts (per 100g or 100mL of product)
    calories_kcal: Optional[float] = None
    protein: Optional[NutrientValue] = None
    fat: Optional[NutrientValue] = None
    carbohydrates: Optional[NutrientValue] = None
    # ... (extensible: e.g. fiber, sugar, sodium, vitamins as needed)
    image_url: Optional[HttpUrl] = None
    ingredients_text: Optional[str] = None
    data_sources: List[str] = []            # e.g. ["USDA_FDC", "OpenFoodFacts", ...]
    upstream_latency_ms: Dict[str, float] = {}  # timing for each source call
```

Normalization: All nutrient quantities (calories, protein, fat, carbs, etc.) in this model are standardized per 100g (or 100mL) of product. This decision is crucial for consistency: different products often report nutrition per serving, but servings vary in size. By converting everything to a common 100g basis, we make the values comparable across products. (Open Food Facts natively uses the 100g standard in its nutriments data, with keys like carbohydrates_100g, etc., and we similarly convert USDA data to per 100g where needed.) The original serving size from the package can be included as an additional field (if we choose, e.g. serving_size_description), but the core fields above will always represent 100g nutritional content.

Data Source Mapping: The table below shows how fields from USDA, OFF, and GS1 map into our canonical model fields:

| **Canonical Field**         | USDA FDC source                                                                                                                                                                                                                                  | Open Food Facts source                                                                                                                        | GS1 GPC source                                                                                                                       | Notes                                                                                                                                                                                                                                                                                                  |
|-----------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **gtin (barcode)**          | Input to API: FDC branded foods data include GTIN as a searchable field (e.g. gtinUpc) if using their search API, but no direct field in response for lookup                                                                                     | Input to API: OFF uses code for the barcode in product data .                                                                                 | Input: GS1 lookup by GTIN triggers category retrieval.                                                                               | All sources share the GTIN as the common key to identify the product.                                                                                                                                                                                                                                  |
| **product_name**            | description – Official product name or food description from FDC record . (For branded foods, this is the name as given by the manufacturer; for generic foods, a commodity name.)                                                               | product_name – Name of product as on package . (OFF also has generic_name or translations, which can be considered.)                          | (No direct product name in GPC) – GPC is taxonomy only, not item-specific.                                                           | Merge rule: prefer USDA’s name if available (authoritative), otherwise use OFF’s name   .                                                                                                                                                                                                              |
| **brand**                   | Branded Foods only: brandOwner field (the manufacturer/brand name) in FDC’s branded food data.                                                                                                                                                   | brands – Brand names string from OFF (could be multiple or comma-separated) .                                                                 | (N/A in GPC)                                                                                                                         | If available from USDA’s data, the official brandOwner is used; otherwise OFF’s brands field is used . (Generic foods may have no brand.)                                                                                                                                                              |
| **category_hierarchy**      | Foundation Foods: foodCategory (broad category) exists for foundational items, but not a detailed hierarchy. Branded Foods: no taxonomy in FDC aside from perhaps food category keywords.                                                        | categories_tags or main_category from OFF (user-generated taxonomy tags). These are informal and multi-language.                              | Primary source: Provided by GS1 GPC as an official hierarchy list (e.g. ["Beverages", "Carbonated Drinks", "Soft Drinks", "Cola"]).  | We use GS1 GPC classification as the authoritative category. If GS1 lookup yields a Brick code, we derive the Segment/Family/Class names. (If GS1 data is unavailable, we could fall back to OFF’s category tags as a last resort, but in principle GS1 is the “source of truth” for classification .) |
| **calories_kcal**           | Available in FDC data as a nutrient (for branded foods, often under labelNutrients.calories.value) . FDC provides values typically per serving; the library or our code will convert this to a per-100g value using serving weight if necessary. | In OFF’s nutriments as energy-kcal_100g (or energy_100g if only kJ given, which we’d convert to kcal). OFF’s data is per 100g by definition . | (No direct nutrition data)                                                                                                           | Merge rule: Use USDA value if present; if USDA is missing this item, use OFF’s energy_kcal. In case of conflict, USDA wins .                                                                                                                                                                           |
| **protein (grams)**         | labelNutrients.protein.value (or in extended nutrients list by nutrient ID) from FDC . Needs conversion to 100g basis if necessary.                                                                                                              | protein_100g in OFF’s nutriments  (already per 100g).                                                                                         | (N/A)                                                                                                                                | Prefer USDA’s protein value; otherwise OFF. Output as {"value": X, "unit": "g"} via NutrientValue model.                                                                                                                                                                                               |
| **fat (grams)**             | labelNutrients.fat.value from FDC (or total lipid nutrient in full data).                                                                                                                                                                        | fat_100g in OFF data .                                                                                                                        | (N/A)                                                                                                                                | Prefer USDA; otherwise OFF. (Could also include breakdown into saturates, etc., if needed later.)                                                                                                                                                                                                      |
| **carbohydrates (grams)**   | labelNutrients.carbohydrates.value from FDC.                                                                                                                                                                                                     | carbohydrates_100g in OFF data .                                                                                                              | (N/A)                                                                                                                                | Prefer USDA; otherwise OFF. (Could be extended to include sugars separately if needed.)                                                                                                                                                                                                                |
| **Additional nutrients...** | FDC’s full nutrient profile via foodNutrients (vitamins, minerals) if we choose to include them.                                                                                                                                                 | Many available in OFF’s nutriments (e.g. fiber, sodium, vitamins) per 100g.                                                                   | (N/A)                                                                                                                                | By design, we can extend the model to include more nutrients (e.g. fiber, sodium, Vitamin A, etc.) as needed. If added, the same rule applies: use USDA’s data when available, otherwise OFF. Each nutrient could also carry a source tag if needed for transparency.                                  |
| **ingredients_text**        | (Not available via FDC) – USDA does not provide ingredient lists in their data.                                                                                                                                                                  | ingredients_text – Full ingredients list from OFF (if provided on the product’s page) .                                                       | (N/A)                                                                                                                                | We rely on OFF for ingredients list since USDA focuses on nutrients, not label contents.                                                                                                                                                                                                               |
| **image_url**               | (Not in FDC)                                                                                                                                                                                                                                     | image_url – URL of the product’s front image (or packaging image) from OFF . OFF often provides images of the product uploaded by users.      | (N/A)                                                                                                                                | Only OFF supplies product imagery. The API will return this URL if available to enrich the consumer experience.                                                                                                                                                                                        |
| **data_sources**            | N/A (constructed field)                                                                                                                                                                                                                          | N/A                                                                                                                                           | N/A                                                                                                                                  | We populate this list to indicate which sources contributed data for the final result. For example, ["USDA_FDC", "OpenFoodFacts", "GS1_GPC"] if all three provided data   . This field is crucial for transparency.                                                                                    |
| **upstream_latency_ms**     | N/A (constructed)                                                                                                                                                                                                                                | N/A                                                                                                                                           | N/A                                                                                                                                  | A dictionary of the time each upstream call took (e.g. {"USDA_FDC": 120.5, "OpenFoodFacts": 80.2, "GS1_GPC": 45.0}) could be included. This helps with monitoring and debugging slowdowns in upstream services .                                                                                       |


Reconciliation Logic: The merging of data happens in a deterministic order (“layered” approach):
1.	Start with an empty CanonicalProduct with the known gtin and default placeholders.
2.	Layer 1: Open Food Facts. If OFF returns a product for the GTIN, populate basic fields from it: product_name, brand, ingredients_text, image_url, and any nutrition fields if USDA might be absent   . Initially use OFF’s nutrition to fill in, but mark them as provisional since USDA may override. Add "OpenFoodFacts" to data_sources.
3.	Layer 2: USDA FDC. If USDA data is available for the GTIN, it overrides or fills in the authoritative fields: set product_name to the official description (replacing the OFF name if one was set) , set the core nutrient fields (calories, protein, etc.) from USDA’s values , overriding any values that might have come from OFF. Add "USDA_FDC" to data_sources.
4.	Layer 3: GS1 GPC. If GS1 classification data is found for the GTIN’s product category, set the category_hierarchy list accordingly . (This might be a list like ["Food/Beverage/Tobacco", "Beverages", "Carbonated Soft Drinks", "Cola Drinks"] – essentially the Segment, Family, Class, Brick names from the GPC schema.) Add "GS1_GPC" to data_sources.
5.	Result: The final CanonicalProduct is then returned. By design, nutrients and name are whatever USDA provided (if it did); missing fields that USDA doesn’t cover (images, ingredients, etc.) will simply be whatever OFF provided. If USDA was missing entirely, OFF’s nutrition (which is per 100g and typically from the product label) will remain in place in those fields. If OFF was missing, we’d still have USDA nutrition but might lack image/ingredients (in that case, those fields stay None).

This layered mapping approach ensures USDA data supersedes less reliable sources for critical facts, while still allowing rich contextual data from OFF to come through for a more complete output   . It also guarantees that every field’s provenance can be traced via data_sources. (In future, if needed, we could even annotate each nutrient with its source or a confidence score. For now, the assumption is that USDA’s presence means high confidence in all overlapping fields.)
Handling Missing or Partial Data: In edge cases where a source doesn’t have some information:
•	If USDA is missing a particular nutrient that OFF has (for example, maybe USDA’s record lacked a newer vitamin but OFF has it from the label), we face a design choice. The simplest approach is to leave that nutrient out (None) or include it from OFF data as a supplement. For this project, we prioritize consistency, so we might choose to include major nutrients from OFF if USDA is missing them, but flag that OFF was used. Because our data_sources list will show both sources, the user implicitly knows not all data came from USDA.
•	If Open Food Facts has data that conflicts with USDA, we take USDA’s value as truth (since OFF is crowdsourced and may contain errors) . The exception is if the USDA data is clearly out of date or incomplete and we trust OFF more for certain fields – for example, ingredients or product naming in local markets. However, for nutrients we stick with USDA if available. In documentation, we will clarify this rule (“USDA overrides OFF for nutrient values if both exist”).
•	If GS1 classification cannot be determined (e.g., our system fails to find a matching category for the GTIN), the category_hierarchy may remain empty or we might attempt a fallback. Potential fallbacks include using the Open Food Facts category tags to at least provide some category. For instance, OFF might label a product with user tags like “Beverages, Soft drinks” – we could include that if GS1 GPC isn’t available. But since the assumption is GS1 is the taxonomy source of truth, we might opt to return an empty category list and consider it an area for future improvement (perhaps integrating a secondary mapping or a machine learning model to predict GPC from text).
•	Partial coverage scenario: Some products might appear in USDA but not OFF (e.g., a generic agricultural commodity) – in that case, we return nutrition and name from USDA, and image_url, ingredients_text remain null (since OFF wasn’t used, and data_sources will only list USDA and GS1). Conversely, if something is only in OFF and not in USDA, we return whatever OFF has (including OFF’s nutriments) and clearly the data_sources will show only OFF (and GS1 if that worked). This way the client is aware of the data’s origin and can gauge quality accordingly.
•	Data freshness & updates: The model does not inherently include timestamps for when the data was last updated by the source, but this could be added (e.g., OFF provides last_modified_datetime, and USDA data has version or publication date). For now, we assume the latest data is fetched on each request (no heavy caching of content, except optional in-memory caching of identical requests). In a production scenario, embedding a last_updated field or at least documenting that “data is current as of each API call” might be worthwhile.


## Example Unified Output

To illustrate, suppose a client calls our API for a product with GTIN 04963406**** (just example digits). The FastAPI endpoint /api/v1/lookup/04963406**** will return JSON like:

```python
{
  "gtin": "04963406021372",
  "product_name": "Coca-Cola Classic",
  "brand": "The Coca-Cola Company",
  "category_hierarchy": [
    "Food/Beverage/Tobacco",
    "Beverages",
    "Carbonated Soft Drinks",
    "Cola Drinks"
  ],
  "calories_kcal": 42.0,
  "protein": { "value": 0.0, "unit": "g" },
  "fat": { "value": 0.0, "unit": "g" },
  "carbohydrates": { "value": 10.6, "unit": "g" },
  "image_url": "https://static.openfoodfacts.org/images/products/049/634/060/21372/front_en.400.jpg",
  "ingredients_text": "Carbonated water, high fructose corn syrup, caramel color, phosphoric acid, natural flavors, caffeine",
  "data_sources": ["USDA_FDC", "OpenFoodFacts", "GS1_GPC"],
  "upstream_latency_ms": { "USDA_FDC": 110.5, "OpenFoodFacts": 95.2, "GS1_GPC": 50.8 }
}
```

Example: The JSON above demonstrates how the final data might look. In this hypothetical case, all three sources contributed: the nutrition values and product name came from USDA (e.g., from a branded foods entry for Coca-Cola Classic), the brand and image and ingredients came from Open Food Facts, and the category hierarchy came from GS1 GPC. The data_sources confirms all were used, and the upstream_latency_ms gives internal performance info. All the nutrient values are per 100 mL (approximately 100g for liquids) – 42 kcal per 100mL – making it easy to compare with any other drink on a 100mL basis. (Note: In practice, a Coca-Cola 12oz serving ~ 355mL would have ~150 kcal, but here we standardized it.)


## FastAPI Service Design and Implementation Details

With the data model defined, the next step is implementing the FastAPI application that uses it. Key aspects of the implementation include project structure, asynchronous data fetching, and the endpoint contract.

Project Structure: A clean project layout is followed to organize code logically:

- app/main.py: Creates the FastAPI app, includes the router for our endpoints.
- app/api/routes.py: Defines the /api/v1/lookup/{gtin} endpoint function.
- app/core/models.py: Contains the Pydantic models (CanonicalProduct, NutrientValue, etc.). [github.com]
- app/services/clients.py: Initializes and configures API clients for USDA, OFF, and GS1. For example, creating a singleton FDCClient with API key, an OFF API client, and a GS1 GPC client.
- app/services/orchestrator.py: Contains the Data Orchestrator logic (mapping/merging function) that converts raw data from the three sources into the CanonicalProduct model. [github.com], [github.com]
- app/config.py: For configuration and secrets (e.g., USDA API key, OFF settings) – could use environment variables and pydantic’s BaseSettings.
- app/tests/: (If writing tests) would include unit tests for the mapper and endpoint, and perhaps integration tests using test data.

By separating the fast API endpoint layer from the data fetching and mapping layer, we achieve a clear separation of concerns:

- The endpoint function simply parses the path parameter and invokes the orchestrator to get data.
- The orchestrator deals with calling external services and merging results.
- The clients abstract details of each external API (so if one changes, we update the client, not the core logic).

Upstream API Clients:

- USDA FDC Client: We utilize the usda_fdc_python library (developed by the project author) to interface with FoodData Central. After instantiating FdcClient with our API key, we likely call a method to fetch food data by GTIN. Since FDC’s API does not have a direct “get by GTIN” endpoint, this may involve using the library’s search functionality. For example, fdc_client.search(<gtin>) which searches for foods matching that code. If a match is found (likely in Branded Foods), the client can then fetch the detailed food item by FDC ID. To streamline this, we might implement a helper method get_nutrition_by_gtin(gtin) that internally does search + lookup and returns a simplified dict of nutrients. In our pseudo-code earlier, we saw fdc.get_nutrition(gtin) being used – this would be such a helper that returns a dictionary containing at least description and labelNutrients for the product if found. The USDA client will raise an error or return None if no food is found for that GTIN. We should handle that outcome gracefully.

- Open Food Facts Client: OFF provides an official Python SDK (openfoodfacts library). We instantiate an API client with a required user_agent string (to identify our app). For example:
```python
import openfoodfactsoff_api = openfoodfacts.API(user_agent="FastAPINutrition/1.0")
```
Using this off_api, we can call off_api.product.get(<gtin>) to retrieve product details by barcode. We may request specific fields to minimize payload (OFF allows a fields= parameter). For our needs, fields like product name, brands, image URL, ingredients text, and nutriments (for calories, protein, etc.) are relevant. If the product exists, OFF returns a JSON (as Python dict) containing these fields. If not, it returns a status indicating product not found. No API key is required for OFF; the data is open. We must be mindful of rate limits or usage terms (it’s community-run), possibly adding a note in our docs to cache frequent results and not overload OFF.
- GS1 GPC Client: The gs1_gpc_python library is used to incorporate the GS1 classification. This is a bit different: GS1 GPC data is static taxonomy data (provided typically as XML or via GS1’s API). The library is primarily for importing that data into a database. For our purposes, we might pre-load the GPC database (maybe SQLite) with the full hierarchy of segments/families/classes/bricks. The tricky part is linking a given GTIN to a GPC Brick code. GTINs themselves do not encode category, so how can we get the GPC Brick for a product? In a real scenario, one would need a separate mapping source or the manufacturer’s data to know the GPC classification of that product. We do not have OneWorldSync (a proprietary source) as it was cost-prohibitive. As a proxy, one approach is to use the product’s category tags or description to infer a likely GPC Brick via some lookup or simple rules. For example, if OFF categories for a GTIN include “Soft drinks”, we might map that to a GPC Brick for soft drinks. However, such inferencing might be beyond scope. Instead, for demonstration, our GPCClient.get_brick(gtin) might use a cached mapping or dummy logic (e.g. using the first few digits to identify the manufacturer and then using a known category for that manufacturer’s product line, or even a hardcoded dictionary for a few example GTINs). In any case, when gs1.get_brick(gtin) is called in our code, it should return a structure like {"hierarchy": ["SegmentName", "FamilyName", "ClassName", "BrickName"], "brick_code": "12345678"}. We then use the hierarchy list in our model. Integration note: Because GS1 GPC is an official standard, it’s good to show we have a slot for it, but the actual mapping from GTIN to GPC might be incomplete unless additional data is available. We document this limitation and possibly include it as a future enhancement (e.g. “integration with a GS1 Data Hub for direct GTIN classification”).

Parallel Asynchronous Calls: FastAPI is built on ASGI and allows async route handlers. In our /lookup/{gtin} endpoint function, we define it with async def and use Python’s asyncio to gather results from the three sources concurrently. For example:

```python
@app.get("/api/v1/lookup/{gtin}", response_model=CanonicalProduct)
async def lookup_product(gtin: str):
    # Fire off all three requests simultaneously
    usda_task = asyncio.create_task(fdc_client.get_nutrition_by_gtin(gtin))
    off_task  = asyncio.create_task(off_api.product.get(gtin))
    gs1_task  = asyncio.create_task(gpc_client.get_brick(gtin))
    # Wait for all to complete (with proper timeout handling in production)
    usda_data, off_data, gs1_data = await asyncio.gather(usda_task, off_task, gs1_task)
    # Merge results into our canonical model
    product = DataOrchestrator.map_to_canonical(gtin, usda=usda_data, off=off_data, gs1=gs1_data)
    return product
```

In the code above, fdc_client.get_nutrition_by_gtin would be our implemented helper (possibly using the usda_fdc_python internally). We launch all three calls without awaiting them immediately, then use asyncio.gather to wait until all three are done. This pattern dramatically improves throughput: the slowest of the three sources will determine the total response time, as opposed to doing them one after another which would sum their latencies. Our goal is to keep typical lookups well under 500 ms, assuming each source responds in ~100-200 ms on average.

We also wrap these calls in timeout and exception handling (not shown in the snippet for brevity). For example, asyncio.wait_for(usda_task, timeout=2.0) could cap a slow USDA call at 2 seconds. If a timeout or error occurs, we would log it and proceed with whatever did return. The map_to_canonical function will simply receive usda=None if USDA failed, and it knows to just not fill those fields (leaving whatever OFF provided or None). This way, the API still returns a 200 OK with partial data rather than failing. We might also include an alert in the response – perhaps an "warnings" field or a special entry in data_sources like "USDA_FDC_error" – but the simplest approach is that missing USDA shows up as its name absent from the data_sources list. For instance, if data_sources is ["OpenFoodFacts","GS1_GPC"] in a response, a client can infer that USDA data is not present (maybe the product wasn’t in USDA or the call failed). In a documentation or version 2, we could make this explicit.

DataOrchestrator Mapper: The merging logic we discussed is implemented in the DataOrchestrator.map_to_canonical method. In code, it will:

```python
class DataOrchestrator:
    @staticmethod
    def map_to_canonical(gtin: str, usda: dict = None, off: dict = None, gs1: dict = None) -> CanonicalProduct:
        product = CanonicalProduct(gtin=gtin, product_name="Unknown Product")
        # Layer 1: OFF data
        if off:
            product.product_name    = off.get('product_name', product.product_name)
            product.brand           = off.get('brands') or product.brand
            product.image_url       = off.get('image_url')
            product.ingredients_text = off.get('ingredients_text')
            # If OFF has nutrient values and USDA is missing, we will use them after checking USDA.
            product.data_sources.append("OpenFoodFacts")
        # Layer 2: USDA data
        if usda:
            product.product_name = usda.get('description', product.product_name)
            # Assume usda['labelNutrients'] exists for branded foods:
            nutrients = usda.get('labelNutrients') or usda.get('foodNutrients') or {}
            if 'calories' in nutrients:
                # handle both possible structures
                product.calories_kcal = nutrients['calories']['value'] if isinstance(nutrients['calories'], dict) else nutrients['calories']
            if 'protein' in nutrients:
                val = nutrients['protein']['value'] if isinstance(nutrients['protein'], dict) else nutrients['protein']
                product.protein = NutrientValue(value=val)
            if 'fat' in nutrients:
                val = nutrients['fat']['value'] if isinstance(nutrients['fat'], dict) else nutrients['fat']
                product.fat = NutrientValue(value=val)
            if 'carbohydrates' in nutrients:
                val = nutrients['carbohydrates']['value'] if isinstance(nutrients['carbohydrates'], dict) else nutrients['carbohydrates']
                product.carbohydrates = NutrientValue(value=val)
            product.data_sources.append("USDA_FDC")
        else:
            # No USDA data; if OFF provided nutrition, use it (already per 100g)
            if off and off.get('nutriments'):
                nutr = off['nutriments']
                if 'energy-kcal_100g' in nutr or 'energy_100g' in nutr:
                    # OFF might have energy in kJ; prefer kcal if present
                    kcal = nutr.get('energy-kcal_100g')
                    if kcal is None:
                        # convert kJ to kcal if needed (1 kcal = 4.184 kJ)
                        kj = nutr.get('energy_100g')
                        kcal = float(kj) / 4.184 if kj is not None else None
                    product.calories_kcal = round(kcal, 2) if kcal is not None else None
                if 'proteins_100g' in nutr:
                    product.protein = NutrientValue(value= nutr['proteins_100g'])
                if 'fat_100g' in nutr:
                    product.fat = NutrientValue(value= nutr['fat_100g'])
                if 'carbohydrates_100g' in nutr:
                    product.carbohydrates = NutrientValue(value= nutr['carbohydrates_100g'])
                # (We could similarly map fiber, sodium etc. if present and needed)
        # Layer 3: GS1 GPC data
        if gs1 and gs1.get('hierarchy'):
            product.category_hierarchy = gs1['hierarchy']
            product.data_sources.append("GS1_GPC")
        return product
```

The above pseudo-code (not an exact copy from the library, but aligned with the plan) demonstrates how the merging occurs step by step. It also shows an important detail: if USDA data is missing, we then rely on OFF’s nutriments to fill the nutrition fields (example code added under the else for USDA absence). This ensures that even if a product is not in FoodData Central, the API still delivers nutrition info as available on the label via OFF – albeit with the caveat that it’s user-contributed data. We also handle unit conversion for energy if only kJ is given by OFF (since many European entries might not list kcal directly).

Pydantic will automatically validate this CanonicalProduct model when returning, ensuring types are correct (e.g., if an upstream provided a string where a float is expected, Pydantic would raise a 422 error). This validation is another safety net to catch any upstream anomalies and maintain data quality in our API.

Endpoint Contract (API Design): The API is designed to be RESTful and versioned:

Endpoint: GET /api/v1/lookup/{gtin} – retrieves the canonical food data for the given GTIN. (We use a path parameter for GTIN to keep it simple and cache-friendly. A query param could be used, but path reads nicely as a resource lookup.)

- Path Format: We expect GTIN-12, GTIN-13, or GTIN-14 strings (numeric). The logic may zero-pad or otherwise normalize them internally if needed. We assume the client will provide a complete barcode number as a string.
- Response: A JSON representation of CanonicalProduct (as shown in the example above). The FastAPI response_model feature will use our Pydantic model to also generate OpenAPI documentation automatically. [github.com], [github.com]
- Response Codes: 200 OK for a successful lookup (even if some sub-data is missing; the response will still be a partial CanonicalProduct). If the GTIN is malformed, FastAPI might throw a validation error (which would be a 422 Unprocessable Entity by default). If something unexpected goes wrong server-side, a 500 might occur, but we aim to handle exceptions and return 200 with partial data whenever possible. We might also implement a custom 404 if none of the sources know the GTIN (i.e., completely unknown product), though one of the three should almost always have it if it’s a real product. Logging will capture if absolutely nothing was found.
- Example Request: GET /api/v1/lookup/04963406021372
- Example Response: (HTTP 200) See JSON example above.
- We also plan supporting endpoints like health checks: e.g., GET /api/v1/health that pings the upstream services or returns the status of the service (useful for DevOps), and possibly a GET /api/v1/version returning the git commit or version number of the deployed service. These aren’t directly about the data, but are part of making it production-grade and transparent.

Asynchronous Pattern Benefits: By using asyncio.gather and non-blocking HTTP calls (e.g., the usda_fdc_client likely uses httpx or requests – if the latter, we might wrap it in loop.run_in_executor or ensure the library is async-friendly), the server can handle many requests concurrently. This is vital if, for instance, we integrate this API into a web or mobile app that scans many barcodes, or an ML pipeline that bulk-fetches data. We also ensure that any CPU-bound work (like perhaps parsing a large JSON) is minimal – mostly just constructing small Python dicts and Pydantic models, which is fast.

Graceful Degradation & Timeouts: We implement timeouts for each external call and use try/except to handle exceptions. For example, if usda_task raises an FdcApiError (perhaps due to an invalid key or 503 status), our gather can be made to return None for that result. The orchestrator then simply doesn’t mark USDA as present. We might additionally append something like "USDA_FDC (error)" in data_sources or a boolean flag usda_available=False in the model if we want to explicitly signal it. The current design opted for implicit indication via missing source in the list, to keep the model clean.

Caching Strategy: To improve performance and reduce load on upstream APIs, we plan to introduce caching at two levels:

- In-memory LRU Cache: During the same run of the application, if the same GTIN is requested repeatedly, we can cache the result of the external calls for a short period. For example, using functools.lru_cache or cachetools.TTLCache in the get_nutrition_by_gtin, get_product, and get_brick functions. Even caching 1000 recent lookups for a few minutes can drastically cut external calls for popular items. Since the data doesn’t change often (food nutrition info is relatively static), caching is safe. The attached design suggests using an LRU cache in Phase 2. [github.com]
- Longer-term cache/persistence: In a production scenario, one might use a persistent cache or database (like Redis or SQLite) to store results, especially for GTINs that are frequently looked up. A nightly job could refresh data for known GTINs. This project’s scope keeps it simple (in-memory only), but a Redis layer is mentioned as a stretch goal for production-hardiness. [github.com]

Pydantic and Validation: The use of Pydantic models for both request and response enforces that our data is well-structured. If upstream returns something unexpected (e.g., a string “>100” for a nutrient value because the label had a “>100” sign), Pydantic will raise a validation error. We can catch such errors and decide how to handle them (perhaps by cleaning the data or defaulting it). This guards our API consumers from inconsistent types. Moreover, the automatic OpenAPI documentation generated will include all our field descriptions, making our API self-documenting for end users.


## Infrastructure & Operations Considerations

Beyond the core functionality, a Lead Engineer level design also covers how this service is deployed, monitored, and maintained in production:


- API Versioning: We prefix the path with /v1 in anticipation of future versions. This allows non-breaking enhancements down the line. Any major changes to the schema or contract would go into /v2 while /v1 could be maintained for backward compatibility. [github.com], [github.com]
- Deployment Architecture: The plan is to containerize the FastAPI app using a Dockerfile (based on a slim Python 3.11 image), and deploy on a cloud platform (the design mentions DigitalOcean App Platform as a cost-effective choice). App Platform can take our Docker image and run it with minimal devops hassle, including handling SSL, scaling, etc. For $5/month we get a basic container that should handle moderate traffic, which is suitable for a portfolio project. [github.com] [github.com], [github.com]
- CI/CD: We integrate with GitHub so that pushing to main triggers an automated deploy. A GitHub Actions pipeline can run tests (pytest) and linting (flake8) before telling DigitalOcean to pull the image. This demonstrates DevOps proficiency: any code change is validated and then goes through continuous delivery. [github.com], [github.com]
- Configuration Management: Secrets like the USDA API Key are stored as environment variables in the cloud platform (not hard-coded). Our code uses something like FDC_API_KEY from env (the usda_fdc_python library can read from env or we pass it explicitly). This avoids committing secrets and aligns with 12-factor app principles.
- Logging and Error Tracking: The service will include structured logging (likely through the standard logging library or an integration like uvicorn logger) to record requests and any errors. For example, if an upstream call fails, we log which GTIN and source failed. In a production setup, we might integrate with monitoring tools or Sentry/GlitchTip for error tracking. The design mentions possibly using SigNoz or GlitchTip for self-hosted monitoring later. [github.com], [github.com]
- Performance Monitoring: Using OpenTelemetry instrumentation for FastAPI can allow distributed tracing. For example, each external call could be a span, so we can see if USDA calls are consistently slower than OFF calls, etc. This is advanced but shows a production mindset. We’d also have a /metrics endpoint exposing Prometheus metrics (via something like starlette_exporter) to track request rates, durations, and upstream timings. [github.com], [github.com] [github.com]
- Health and Freshness: We provide a /health endpoint that checks basic connectivity to each source (maybe by performing a lightweight request or checking a cached timestamp). Additionally, a data freshness concept is introduced: we could periodically log or expose when we last updated our GS1 taxonomy or if the OFF data for a product might be stale (OFF has timestamps). While not implemented from day one, the design envisions a “data freshness” telemetry endpoint that could report if, say, our local GPC database is using the latest schema version, or how long ago we saw a given product updated on OFF. This is about being transparent that our data is up-to-date. [github.com] [github.com], [github.com]
- Security: Since this is a public-facing API, we ensure it’s in HTTPS (DO App Platform does this automatically). No auth is required for this read-only data API (all sources are public data). However, we must be mindful of not exposing any personal or secure info – which we do not, since all data is public food information. We could implement rate limiting to prevent abuse (perhaps DO or a proxy can handle that). We also consider CORS settings: likely we’ll allow all origins (*) for GET requests unless we want to restrict it (the design notes adding CORS restrictions as a stretch goal). [github.com]
- Compliance: Although not directly dealing with user data, the architecture is kept SOC2-compliant ready – using environment secrets, minimal PII (really none), and the container environment is isolated. The design highlights that having a single canonical model also makes it easier to implement any needed data masking or compliance rules in one place (for instance, if we did ever handle user-contributed data, we could sanitize it in the model). [github.com]
- Documentation & Demo: Thanks to FastAPI, we get an automatic interactive docs (Swagger UI) at /docs. We will enhance the documentation with metadata: each field in the Pydantic model has a description (as seen with category_hierarchy field above where a description is provided). We can add examples to the docstrings or OpenAPI schema. We’ll also probably write a detailed README and a series of blog-style articles (which is actually part of the goal – to produce an article series demonstrating all these aspects). The README might be structured as a technical decision record, explaining why we chose FastAPI, how we handled data normalization, etc..

The entire project is organized not only to solve the technical problem but to showcase engineering best practices. It connects to the author’s past experience (e.g. prior work with similar lookup APIs and data pipelines) and demonstrates a modern cloud-native approach. In summary, this unified nutrition API will stand as a robust, well-architected example of integrating multiple data sources, applying data engineering to normalize and reconcile information, and delivering it through a high-performance API – all with an eye toward maintainability, transparency, and scalability.

##  Unified Food Intelligence API

*A Production‑Grade FastAPI Aggregator for USDA FDC, Open Food Facts, and GS1 GPC* and other data sources.

## Purpose

This project demonstrates Lead / Principal‑level platform, API, and data‑engineering skills by designing and implementing a **canonical food lookup API**.

The API consolidates **three heterogeneous public data sources** into a single, stable, versioned contract suitable for analytics pipelines and ML feature generation.

## Field‑Level Source Mapping

| Canonical Field | USDA FDC | Open Food Facts | GS1 GPC |
|----------------|----------|-----------------|---------|
| gtin | search key | code | lookup key |
| product_name | description | product_name | — |
| brand | brandOwner | brands | — |
| category_hierarchy | — | fallback only | authoritative |
| calories_kcal | label nutrients | energy-kcal_100g | — |
| protein | label nutrients | proteins_100g | — |
| fat | label nutrients | fat_100g | — |
| carbohydrates | label nutrients | carbohydrates_100g | — |
| ingredients_text | — | ingredients_text | — |
| image_url | — | image_url | — |

## Conflict Resolution Rules

1. USDA overrides OFF for all nutrition conflicts
2. OFF nutrition used only when USDA is missing
3. Ingredients and images always sourced from OFF
4. GS1 taxonomy is never overridden
5. Missing data does **not** fail the request

## Async Orchestration Pattern

```python
@app.get("/api/v1/lookup/{gtin}", response_model=CanonicalProduct)
async def lookup_product(gtin: str):
    usda_task = asyncio.create_task(fdc.get_by_gtin(gtin))
    off_task  = asyncio.create_task(off.get_product(gtin))
    gs1_task  = asyncio.create_task(gs1.get_brick(gtin))

    usda, off, gs1 = await asyncio.gather(
        usda_task, off_task, gs1_task, return_exceptions=True
    )

    return DataOrchestrator.map_to_canonical(
        gtin=gtin, usda=usda, off=off, gs1=gs1
    )
```

## Data Orchestrator

```python
class DataOrchestrator:
    @staticmethod
    def map_to_canonical(gtin, usda=None, off=None, gs1=None):
        product = CanonicalProduct(gtin=gtin, product_name="Unknown")

        if off:
            product.product_name = off.get("product_name", product.product_name)
            product.brand = off.get("brands")
            product.image_url = off.get("image_url")
            product.ingredients_text = off.get("ingredients_text")
            product.data_sources.append("OpenFoodFacts")

        if usda:
            product.product_name = usda["description"]
            nutrients = usda.get("labelNutrients", {})
            product.calories_kcal = nutrients.get("calories", {}).get("value")
            product.protein = NutrientValue(
                value=nutrients.get("protein", {}).get("value", 0)
            )
            product.data_sources.append("USDA_FDC")

        if gs1:
            product.category_hierarchy = gs1["hierarchy"]
            product.data_sources.append("GS1_GPC")

        return product
```

## Phases

- Phase 1: Foundation
Project scaffolding and core development. Set up the FastAPI project, define Pydantic models (CanonicalProduct, etc.), implement the Data Orchestrator merge logic, and get basic integration working with the USDA and GS1 libraries plus an HTTP client for OFF.
- Phase 2: Robustness
Enhance the API for production use. Introduce asyncio gather for parallel calls, add graceful error handling (circuit breaker) so failures degrade gracefully, implement in-memory caching for performance, add input validation and helpful error messages, and version the API under /v1. Also implement health and version endpoints for operability.
- Phase 3: Deployment
Containerize and deploy the service. Create a multi-stage Dockerfile (using Python 3.11 slim), and deploy on DigitalOcean App Platform via an IaC config (`app.yaml`). Set up the USDA API key in the environment. Configure GitHub Actions for CI/CD so that new commits run tests and automatically deploy on success.
- Phase 4: Observability & Polish
Add production monitoring features. Integrate OpenTelemetry instrumentation for tracing FastAPI requests and timing each external call. Add a /metrics endpoint (Prometheus format) to expose performance metrics. Ensure the response includes upstream_latency_ms for insight into external calls. Polish the OpenAPI docs with detailed field descriptions and metadata (e.g., contact info, project URL) and include a custom docs page if needed.
- Phase 5: Stretch Goals
Explore advanced improvements. For example, integrate a Redis cache for cross-instance caching, tighten CORS or add authentication if making a public API service, improve logging/monitoring (e.g., shipping logs to an external system or integrating with an error tracker), and add a data freshness dashboard or endpoint to report how up-to-date each source’s data is in our system. Also consider expanding to more USDA data types (like supporting branded food ingredients or LanguaL factors) for a bigger data engineering challenge.

By following this phased plan, we ensure that the project not only meets its functional requirements (consolidating three data sources) but also demonstrates the qualities of a production-ready platform: correctness, performance, resilience, clarity in code, and operability in deployment. Each phase builds on the prior, from getting the basics right in Phase 1 to adding bells and whistles (that truly matter for a lead-level project) by Phase 4 and 5.

In conclusion, this unified nutrition lookup API will serve as a compelling portfolio piece. It tackles a real-world integration problem with elegance: a clear data model, well-defined mapping from multiple sources, intelligent conflict resolution in favor of high-quality data, and a modern, async-enabled API implementation. All of this is backed by good software engineering practices (version control, CI/CD, documentation, testing) and cloud deployment. The end result is an API that a client or data scientist can call with a barcode and get a rich, reliable set of information about that food product – demonstrating full-stack skill from data engineering through API design and deployment.

## Why Markdown

- Native to GitHub
- Diff‑friendly
- Renders cleanly in VS Code
- Ideal for ADRs and architecture docs
- Reusable for blog posts without rewriting
