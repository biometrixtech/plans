import csv
import os
import json
os.environ['ENVIRONMENT'] = 'test'
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from models.insights_tsv_entities import InsightsParentDataItem, InsightsChildDataItem, InsightsCTA, InsightsDataItem, InsightsPlansDataItem, InsightsPlotsDataItem, InsightsTrendsDataItem, TriggerCollection

with open('Fathom Content Management System - Insights & Trends.tsv', newline='') as tsvfile:
    trigger_reader = csv.DictReader(tsvfile, dialect='excel-tab')
    row_count = 0
    trigger_list = []
    for row in trigger_reader:
        plans_data_item = InsightsPlansDataItem(row["Plans Priority Styling"], row["Plans Content to Pass"], row["Present In Plans"], row["CLEARED Title"])
        parent_data_item = InsightsParentDataItem(row["Parent Enum"], row["NEW, FIRST TIME Parent - Title"],
                                                  row["NEW, FIRST TIME Parent - Body"],
                                                  row["NEW, SUBSEQUENT Parent - Title"],
                                                  row["NEW, SUBSEQUENT Parent - Body"],
                                                  row["CLEARED Parent - Body"])
        child_data_item = InsightsChildDataItem(row["NEW, FIRST TIME Child - Title"],
                                                  row["NEW, FIRST TIME Child - Body"],
                                                  row["NEW, SUBSEQUENT Child - Title"],
                                                  row["NEW, SUBSEQUENT Child - Body"],
                                                  row["CLEARED Child - Body"])

        plans_data_item.parent_data_item = parent_data_item
        plans_data_item.child_data_item = child_data_item

        trends_data_item = InsightsTrendsDataItem(row["Trends Priority Styling"], row["Trends Content to Pass"],
                                                  row["Present in Trends"], row["NEW Title"], row["NEW Body"],
                                                  row["ONGOING Title"], row["ONGOING Body"], row["POS CHANGE Title"],
                                                  row["POS CHANGE Body"], row["NEG CHANGE Title"],
                                                  row["NEG CHANGE Body"], row["Trends CLEARED Title"],
                                                  row["Trends CLEARED Body"])
        plots_data_item = InsightsPlotsDataItem(row["Unit of Aggregation"], row["Visualization Type"],
                                                row["Visualization Range"], row["Overlay Variable"], row["Plots Title"])

        cta_data_item = InsightsCTA(row["Input"], row["Heat"], row["Warmup"], row["Cooldown / Active Recovery"],
                                    row["Active Rest"], row["Ice"], row["CWI"],
                                    row["Increase Default Recommended Comp. of Activity"])
        insights_data_item = InsightsDataItem(row["Trigger Enum"], row["Trend Type"], row["Triggers"],
                                              row["Goal Names"], row["Length of Impact"],
                                              row['Data Source to inform "All Good"'],
                                              row["Insight Priority within Plans"],
                                              row["Insight Priority within Trend Type"])
        insights_data_item.plans_data_item = plans_data_item
        insights_data_item.trends_data_item = trends_data_item
        insights_data_item.cta_data_item = cta_data_item
        insights_data_item.plots_data_item = plots_data_item
        trigger_list.append(insights_data_item)
    trigger_collection = TriggerCollection(trigger_list)
    json_output = trigger_collection.json_serialise()
    json_string = json.dumps(json_output, indent=4)
    f1 = open("triggers.json", 'w')
    f1.write(json_string)
    f1.close()