# HMT-Tic-Tac-Toe
Final Project for Human Machine Teaming Class Spring 2026

## Hypothesis and Papers

Our hypothesis are the following:
- __A workload-aware chatbot that provides explainable move rationales a will result in higher team performance than a non-explainable assistant.​__
- __A context aware machine is more efficient in building trust than one lacking context.​__

The following papers support these hypothesis:
- [Adaptive Task Allocation in Human-Machine Teams
with Trust and Workload Cognitive Models
](https://www.profs.polymtl.ca/jerome.le-ny/docs/proceedings/2020_SMC_trustHA.pdf)
- [Impact of Team Models in Hierarchical Human-Agent Decision-Making
Teams
](https://www.scitepress.org/Papers/2025/130974/130974.pdf)
- [Neuroadaptive User Experience Framework for Human–AI Teaming in Defense Industry](https://journal.formosapublisher.org/index.php/ijar/article/view/15476/14417)
- [Interfaces t faces to Enhance P o Enhance Performance in Human-AI T formance in Human-AI Teams
Conducting Safety-Critical Military Operations: A Route
Reconnaissance Use Case](https://open.clemson.edu/cgi/viewcontent.cgi?article=5224&context=all_dissertations)


## Running the App

### For Devs
Follow these steps to setup the envoirment needed to run the application
1. Create a venv
```bash
python -m venv .venv
```
2. Enter your .venv (this will be OS specific)
3. Install all the requirements
```bash
pip install -r requirements.txt
```
3. Create a .env file in the tictactoe_api directory and add the following values:
```bash
LLM_BASE_URL = "<BASE_URL>"
LLM_API_KEY = "<API_KEY>"
LLM_MODEL = "<MODEL>"
```
> __*Note:*__ The LLM_MODEL can be left empty to allow for automatic selection of the default model
4. Run the Application 
```bash
python manage.py runserver
```

## TechStack
- Python 3.14.0
- Django 5
- OpenAI API
- Local LLM: [lfm2-2.6b-mr-tictactoe@q8_0](https://huggingface.co/mradermacher/LFM2-2.6B-mr-tictactoe-GGUF)