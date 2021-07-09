# hn-whoshiring-analysis
## Analysis of HackerNews Who's Hiring posts using Interactive Python

Related [blog post](https://iblaine.github.io/hackernews-whos-hiring-analysis/)

### Quick steps on how to use
1. git clone git@github.com:iblaine/hn-whoshiring-analysis.git
2. python -m venv env
3. source env/bin/activate
4. pip install -r requirements.txt
5. code hn_hiring_analysis.py
6. click "Run Cell" as needed

### What does this notebook do?
* Load [HackerNews Who is hiring](https://news.ycombinator.com/item?id=27699704) posts from Jan 2013 to July 2021
* Parse the data, add to a dict stored as hn_metrics.json
* Denormalize data into a dataframe, make the data available for analysis

### Notes
* Every month has about 1,000 items
* The data is not structured very well, which limits a lot of analysis

### Example of data produced by this analysis...
<table>
  <tr>
    <td><img src="https://github.com/iblaine/hn-whoshiring-analysis/blob/main/charts/data-top-posters.png" width="400"></td>
    <td><img src="https://github.com/iblaine/hn-whoshiring-analysis/blob/main/charts/graph-dataengineer-by-month.png" width="400"></td>
    <td><img src="https://github.com/iblaine/hn-whoshiring-analysis/blob/main/charts/graph-hnwhoshiring-by-month.png" width="400"></td>
    <td><img src="https://github.com/iblaine/hn-whoshiring-analysis/blob/main/charts/graph-remote-by-month.png" width="400"></td>
  </tr>
</table>

### Walkthrough...<br>
<img src="https://github.com/iblaine/hn-whoshiring-analysis/blob/main/walkthroughs/hn-analysis-walkthrough.gif" width="400">

### Sample data, in case you want a quick look at what may be available
```
[
   "2021-06-01"
]{
   "company_names":{
      "Tourmaline Labs":1,
      "Dr. Bill / RBC Ventures":1,
      "Flowdash":1,
      "Koddi":1,
      "HVN":1,
      "Sparrow":1
   },
   "locations":{
      "Senior Back End and Mobile":1,
      "Senior Software Engineers, Tech Leads, Engineering Managers, Product Designers":1,
      "Software Developer":1,
      "San Francisco Bay Area":1,
      "Frontend Tech Lead, Full-Stack, Backend":1
   },
   "position_types":{
      "ML & Backend engineers":1,
      "Remote (EU) or Onsite (Berlin, Germany)":1,
      "Full-time, REMOTE in US":1,
      "Australia, Remote":1,
      "NYC":3,
      "REMOTE - US ONLY":1,
      "React, TypeScript, Tailwind, C#, React Native - both local and remote (Lancaster, PA":1,
      "Sarasota, FL":1
   },
   "position_names":{
      "<a href=\"https://vertexvis.com\" rel=\"nofollow\">https://vertexvis.com</a>":1,
      "ONSITE (post-covid)":2,
      "Software Developer":1,
      "Portland or Remote":1,
      "<a href=\"http://synth.earth\" rel=\"nofollow\">http://synth.earth</a>":1,
      "\\"
   },
   "search_results":{
      "data engineer":{
         "cnt_total":91,
         "cnt_unique":72
      },
      "software engineer":{
         "cnt_total":626,
         "cnt_unique":369
      },
      "full stack":{
         "cnt_total":174,
         "cnt_unique":131
      },
      "fullstack":{
         "cnt_total":77,
         "cnt_unique":59
      }
   }
}
```
