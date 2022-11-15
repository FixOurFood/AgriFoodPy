%%%%%%%% Wed 9 Nov 2022

%%%% Read in the latest NDNS data and do some plots

% Misc stuff that might be useful
% https://www.gov.uk/government/statistics/ndns-results-from-years-9-to-11-2016-to-2017-and-2018-to-2019
% specifically these two zip files / folders:
% NDNS_from_years_1_to_9_data_tables__1_
% NDNS_results_from_years_9_to_11_combined_appendices__2_
% This document is also worth reading NDNS_UK_Y9-11_report.pdf
% ... hmm the above don't actually contain the data...

% Download the files from
% https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=6533
% ``The citation for this study is: University of Cambridge, MRC Epidemiology Unit, NatCen Social Research. (2022). National Diet and Nutrition Survey Years 1-11, 2008-2019. [data collection]. 19th Edition. UK Data Service. SN: 6533, DOI: 10.5255/UKDA-SN-6533-19''
% ``Copyright: Crown copyright held jointly with the National Centre for Social Research. Crown copyright material is reproduced with the permission of the Controller of HMSO and the Queen s Printer for Scotland.''
% Click on the purple 'Access data' button
% Create an account on NatCen if you don't already have one
% Add the data to an existing project or start a new one
% Download the 'TAB' format [not sure if the others are better?]

clear; cd('c:\Users\Sarah Bridle\Dropbox\work\code\'); slb_matlab_setup;

datadir = 'C:\Users\Sarah Bridle\Dropbox\scratch\food\NDNS\dl_20221109\UKDA-6533-tab\tab\';

filenames = ls(datadir);
% * annoyingly the filenames are not in the same format for all years
% so can't just change 'year' and redo the analysis for different years
% without taking this into account e.g. 
% 'ndns_yr11_nutrientdatabank_2021-03-19.tab' cf
% 'ndns_yr9_nutrientdatabank.tab' grr
% plough on regardless just for year 11
% * remove the '.tab' from the filestems in case we want to use a different
% format file one day
nutrientdatabank_filestems = ...
    {'ndns_yr1_nutrientdatabank', ...
    'ndns_yr2_nutrientdatabank', ...
    'ndns_yr3_nutrientdatabank', ...
    'ndns_yr4_nutrientdatabank', ...
    'ndns_yr5_nutrientdatabank', ...
    'ndns_yr6_nutrientdatabank', ...
    'ndns_yr7_nutrientdatabank', ...
    'ndns_yr8_nutrientdatabank', ...
    'ndns_yr9_nutrientdatabank', ...
    'ndns_yr10_nutrientdatabank_2021-03-19',...
    'ndns_yr11_nutrientdatabank_2021-03-19'};
% * The following line of code will look like overkill - until you see the
% other filenames below.
% old format: nutrientdatabank_fileyears = {[1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11]};
% Create a lookup table to know which file corresponds to which year
% (could automate this, but keep it general for potential new 
% filename formats instead)
nutrientdatabank_fileyears = [1 2 3 4 5 6 7 8 9 10 11];
% * the years are grouped for some files and not for others - grr
% so the nutrientdatabank has one file per year, whereas the 
% dayleveldietarydata_foods_uk has one file for years 1-4, one for 5-6 etc
% not sure how to best manage this internally?
dayleveldietarydata_foods_filestems = {...
    'ndns_rp_yr1-4a_dayleveldietarydata_foods_uk.tab', ...
    'ndns_rp_yr5-6a_dayleveldietarydata_foods', ...
    'ndns_rp_yr7-8a_dayleveldietarydata_foods', ...
    'ndns_rp_yr9-11a_dayleveldietarydata_foods_uk_20210831', ...
    };
% (* Could probably automate this next line - but I don't fully 
% trust the format of future filenames to follow the same convention
% anyway, so I'm doing it by hand)
% This format turned out not to be easy to use, so turn it around: dayleveldietarydata_foods_fileyears = {[1 2 3 4], [5 6], [7 8], [9 10 11]};
dayleveldietarydata_foods_fileyears = [1 1 1 1 2 2 3 3 4 4 4];
dayleveldietarydata_nutrients_filetsems = {...
    'ndns_rp_yr1-4a_dayleveldietarydata_nutrients_uk_v2', ...
    'ndns_rp_yr5-6a_dayleveldietarydata_nutrients_v2', ...
    'ndns_rp_yr7-8a_dayleveldietarydata_nutrients', ...
    'ndns_rp_yr9-11a_dayleveldietarydata_nutrients_uk_20210831', ...
    };
% old format: dayleveldietarydata_nutrients_fileyears = {[1 2 3 4], [5 6], [7 8], [9 10 11]};
dayleveldietarydata_nutrients_fileyears = [1 1 1 1 2 2 3 3 4 4 4];
foodleveldietarydata_filestems = {...
    'ndns_rp_yr1-4a_foodleveldietarydata_uk_v2', ...
    'ndns_rp_yr5-6a_foodleveldietarydata_v2', ...
    'ndns_rp_yr7-8a_foodleveldietarydata', ...
    'ndns_rp_yr9a_foodleveldietarydata_uk_20210831', ...
    'ndns_rp_yr10a_foodleveldietarydata_uk_20210831', ...
    'ndns_rp_yr11a_foodleveldietarydata_uk_20210831', ...
    };
% old format: foodleveldietarydata_fileyears = {[1 2 3 4], [5 6], [7 8], [9], [10], [11]};
foodleveldietarydata_fileyears = [1 1 1 1 2 2 3 3 4 5 6];
hhold_filestems = {...
    'ndns_rp_yr1-4a_hhold_uk', ...
    'ndns_rp_yr5-6a_hhold', ...
    'ndns_rp_yr7-8a_hhold', ...
    'ndns_rp_yr9-11a_hhold_20210831', ...
    };
% old format: hhold_fileyears = {[1 2 3 4], [5 6], [7 8], [9 10 11]};
hhold_fileyears = [1 1 1 1 2 2 3 3 4 4 4];
indiv_filestems = {...
    'ndns_rp_yr1-4a_indiv_uk', ...
    'ndns_rp_yr5-6a_indiv', ...
    'ndns_rp_yr7-8a_indiv', ...
    'ndns_rp_yr9-11a_indiv_20211020', ...
    };
% old format: indiv_fileyears = {[1 2 3 4], [5 6], [7 8], [9 10 11]};
indiv_fileyears = [1 1 1 1 2 2 3 3 4 4 4];
personleveldietarydata_filestems = {...
    'ndns_rp_yr1-4a_personleveldietarydata_uk_v2', ...
    'ndns_rp_yr5-6a_personleveldietarydata_v2', ...
    'ndns_rp_yr7-8a_personleveldietarydata', ...
    'ndns_rp_yr9-11a_personleveldietarydata_uk_20210831', ...
    };  
% old format: personleveldietarydata_fileyears = {[1 2 3 4], [5 6], [7 8], [9 10 11]};
personleveldietarydata_fileyears = [1 1 1 1 2 2 3 3 4 4 4];
% * err what is this weights thing that exists only for year 1-3?!
indiva_weights_filestems = {...
    'ndns_yr1-3indiva_weights', ...
    };
% old format: indiva_weights_fileyears = {[1 2 3]};
indiva_weights_fileyears = [1 1 1 0 0 0 0 0 0 0 0];

% Try to read in the personleveldietarydata for year 11
iyear = 11;
ifile = personleveldietarydata_fileyears(iyear);
personleveldietarydata_filestem = personleveldietarydata_filestems{ifile};
NDNSdata.personleveldietary = readtable([datadir,personleveldietarydata_filestem,'.tab'],...
    'FileType','delimitedtext');

% Take a look
NDNSdata.personleveldietary(1:10,:)
NDNSdata.personleveldietary.Properties.VariableNames'

% Plot kcal
clf
hist(NDNSdata.personleveldietary.Energykcal,100)
hold on
v = axis;
plot(rda*[1 1], [v(3) v(4)],'r--')
% Peaks way lower than 2500 -> underreporting and also children
% so take other plots with this grain of salt for now..

% 'phylloquinone' = vitamin K(1), apparently 
% also "vitamin K1 and vitamin K2 (menaquinone-4 (MK-4) and menaquinone-5 to
% 10 (MK-5–10))"
% Isn't in there. 
% switch to a different nutrient
% Vitamin E https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9141080/

% Vitamin E
x = NDNSdata.personleveldietary.VitaminEmg;
% "The amount of vitamin E you need is: 4mg a day for men 3mg a day for
% women" - https://www.nhs.uk/conditions/vitamins-and-minerals/vitamin-e/
rda_uk = 3.5;
% ``The Recommended Dietary Allowance (RDA) for vitamin E for males and
% females ages 14 years and older is 15 mg daily (or 22 international
% units, IU), including women who are pregnant. Lactating women need
% slightly more at 19 mg (28 IU) daily.'' - https://www.hsph.harvard.edu/nutritionsource/vitamin-e/#:~:text=Recommended%20Amounts,mg%20(28%20IU)%20daily.
% https://ods.od.nih.gov/factsheets/VitaminE-HealthProfessional/
rda_us = 15;

clf
hist(x,100)
hold on
v = axis;
plot(rda_uk*[1 1], [v(3) v(4)],'r:')
plot(rda_us*[1 1], [v(3) v(4)],'m--')
legend('NDNS','UK RDA','US RDA')

% Find the fraction of people not meeting uk rda requirements
length(find(x<rda_uk)) / length(x) 
% 0.0396
% Find the mean amount in the lowest quintile
lowest_quintile_cut = prctile(x,20)
mean_lowest_quintile_cut = mean(x(find(x<lowest_quintile_cut)))
mean_lowest_quintile_cut / rda_uk
% 1.225 i.e. above the RDA - though 
mean_lowest_quintile_cut / rda_us
% 0.2858

% Vitamin A
x = NDNSdata.personleveldietary.VitaminAretinolequivalents_g; 
x_max_plot = 3000;
% ``The Recommended Dietary Allowance for adults 19 years and older is 900
% mcg RAE for men (equivalent to 3,000 IU) and 700 mcg RAE for women
% (equivalent to 2,333 IU'' - https://www.hsph.harvard.edu/nutritionsource/vitamin-a
rda_us = (900 + 700)/2; % convert from mcg to g by dividing by 1000
% ``The amount of vitamin A adults aged 19 to 64 need is: 700 µg a day for men 600 µg a day for women''
rda_uk = (700 + 600)/2; 
clf
hist(x,1000)
% This must be in mcg not g
hold on
v = axis;
axis([v(1) x_max_plot v(3) v(4)])
plot(rda_uk*[1 1], [v(3) v(4)],'r:')
plot(rda_us*[1 1], [v(3) v(4)],'m--')
legend('NDNS','UK RDA','US RDA')

% Find the fraction of people not meeting uk rda requirements
length(find(x<rda_uk)) / length(x) 
% Find the mean amount in the lowest quintile
lowest_quintile_cut = prctile(x,20)
mean_lowest_quintile_cut = mean(x(find(x<lowest_quintile_cut)))
mean_lowest_quintile_cut / rda_uk
% 0.3551  

%