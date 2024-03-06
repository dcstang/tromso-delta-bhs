import yaml

def getProductFromDag(searchString):
    with open("pipeline.yaml", "r") as stream:
        try:
            pipelineDag = (yaml.safe_load(stream))
        except yaml.YAMLError as exc:
            print(exc)

    targetTask = [x for x in pipelineDag["tasks"]
                  if searchString in x["name"]][0]["product"]        
    return targetTask

def tidyOutputName(outputPathText, clearString):
    return outputPathText.replace(clearString, "").strip().lower().replace("(", "").replace(")", "").replace(" ", "_")