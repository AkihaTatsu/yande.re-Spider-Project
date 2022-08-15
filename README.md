# yande.re-Spider-Project
A personal development of the experiment of the Data Analysis course of USTC.

Structure has been rewritten for better extensibility.

## Description

### Algorithm
This web crawler will use the keyword (the first keyword if there are multiple ones) to fetch all searching result pages in [yande.re](https://yande.re/), and acquire full-size picture URLs to download.

If use multiple keywords, only pictures whose tags include all keywords will be downloaded. It is recommended to put the keyword with least searching results first, as it will reduce number of searching result pages to fetch.

Two types of crawling are provided:
+ 'Basic' only downloads pictures to a certain folder.
+ 'Classify by characters' will move pictures with character tags to corresponding character tag folders.

The details of downloading process will be recorded in .log file in the downloading folder. It is recommended to check out errors after downloading finishes.

## Running

### Download pictures
Running main.py will start a new downloading project:
```bash
python Main.py
```
You will be provided with a configuration interface, in which you can configure the arguments before start downloading.

Pay attention that the default project saving path is: **./DOWNLOAD/**

Also, you can configure parameters when running .py in console like:
```bash
python Main.py --kw "uma_musume_pretty_derby,uniform"
               --skip-kw kitasan_black_(umamusume)
               --start-page 2
               --finish-page 5
               -no-e
               --score 10
               --t 15
               -r
               --thread-num 3
               --proxy-type https
               --proxy http://127.0.0.1:1080
               --path "C:\Users\Public\Downloads\Yandere-Spider"
```
For full description, use ```python main.py -h``` or ```python main.py -help```.

**It is highly advised to set a small thread num and large delay time in order not to generate exceedingly frequent requests.**

### Use config files to continue download
Once arguments are set, a ```{start time} {keywords} config.json``` will be created to record current progress.

If downloading process is interrupted or some pictures are failed to download, run
```bash
python Config_Parse.py
```
and input the json file name.

Also you can use
```bash
python Config_Parse.py --json-path config.json
```
to load .json file. The downloading process will continue from the progress recorded.
