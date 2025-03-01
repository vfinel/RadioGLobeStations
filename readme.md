This reository gathers code to use the [radio garden](https://radio.garden) API to get a list of radio stations usable by the [radio globe](https://www.instructables.com/RadioGlobe-Spin-to-Search-Over-Web-Radio-2000-Stat/). 

Credits to [johnmduffy76](https://github.com/johnmduffy76) who developed the code and shared it [here](https://github.com/DesignSparkRS/RadioGlobe/issues/7#issuecomment-2676891014). Many thanks ! I did minor modifications so that the code can be ran on the raspberry pi directly and added this readme.


# instructions to run on the pi 
- ssh into your pi 

- run tmux (optionnal but recommended):
```tmux```

Why [tmux](https://github.com/tmux/tmux/wiki) ? The python script takes time to check all radio stations, and if your ssh connection is disconnected during that time (for example because your compute goes offline), without tmux, the python code running on the raspberry pi would be killed. Read more about this [here](https://docs.dkrz.de/blog/2022/tmux.html).

If you don't have it already, install tmux : ```sudo apt install tmux```

If you ran the python code and closed your ssh connection while it was running, after reconnecting to the pi via ssh you can reattach to the shell where python is running using with ```tmux a -t 0```


# first installation on the radio globe's raspberry pi 
The instructions below assumes that you have ssh'ed into your pi.

- clone the repo:
```git clone git@github.com:vfinel/RadioGLobeStations.git```

- cd to the repo:
```cd RadioGlobeStations ```

- install python3-venv if necessary:
```sudo apt-get install python3-venv```

- create a venv:
```python -m venv .venv```

- install dependencies in the venv:
```pip install requests pandas pycountry unidecode openpyxl```


# usage 
The instructions below assumes that you have ssh'ed into your pi.

- activate venv:
```source .venv/bin/activate```

- download list of stations from radio garden, check urls and build Excel file: 
```python radio_garden_processor.py```

- edit the Excel file manually if you have reasons to do it 

- convert Excel file to json for the radio globe software:
```python xlsx_to_json.py```

- move the ```stations.json``` file to your RadioBlobe software folder.

- You are done!

## explanations
The code has been written by from [johnmduffy76](https://github.com/johnmduffy76), below the explanations from the [github issue](https://github.com/DesignSparkRS/RadioGlobe/issues/7):

The script ```radio_garden_processor.py``` will:
- look at Radiogarden's API and build an Excel table with 5 columns of data
- indicate all failed links which could be re-examined again later at another time of day
- reformat all non-Latin characters and translates the titles to English. 

Then the script ```xlsx_to_json.py``` formats the XLSX format to JSON, which the RadioGlobe can understand.



# future improvements 
- note from [johnmduffy76](https://github.com/johnmduffy76): 

> "One issue is that this creates a .json file with many, many more city locations than the original .json file that the development team originally created. Consolidating these together within a nearby large town/city is probably preferred to having a plethora of small towns where you only see a few stations. If this is the best way forward, it still needs to be done."
- save progress in a csv file and append only the new stations (otherwise saving the excel takes a longer and longer time) and convert to excel at the end of the for loop 
- print execution time of ```radio_garden_processor.py```
- use [tqdm](https://tqdm.github.io/) to estimate remaining time (requires running the for loops once without streaming to count the number of radio stations to be scanned -or parse json smartly using pandas)
- use parallel for loops to speed up the process 
