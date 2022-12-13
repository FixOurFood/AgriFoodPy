%%%%%%%% Tue 13 Dec 2022

%%%% Make a plot using Defra crop yield data

clear; cd('c:\Users\Sarah Bridle\Dropbox\work\code\'); slb_matlab_setup;

% Download all the files from here:
% https://www.data.gov.uk/dataset/c5004352-fe97-4bd5-8f2e-02554c02c2ba/june-survey-of-agriculture-and-horticulture-uk
% This took a while, so you can also get it from my downloads here: https://www.dropbox.com/sh/os7aasx08mexqu6/AAB8PqOyS-fGcgd9RHNOdz0za?dl=0
datadir = 'C:\Users\Sarah Bridle\Dropbox\scratch\food\UK agri data gov\Defra yields regional 2015\';

% This is a paste from the website of the info - could be tidied up a bit
%strings = {...
%    'Regional Oil Seed Rape; Areas yields and production, Format: CSV, Dataset: June Survey of Agriculture and Horticulture, UK	CSV	08 October 2015	PreviewCSV 'Regional Oil Seed Rape; Areas yields and production', Dataset: June Survey of Agriculture and Horticulture, UK', ...
%    'Regional oats; Areas yields and production, Format: CSV, Dataset: June Survey of Agriculture and Horticulture, UK	CSV	08 October 2015	PreviewCSV 'Regional oats; Areas yields and production', Dataset: June Survey of Agriculture and Horticulture, UK', ...
%    'Regional total barley; Areas yields and production, Format: CSV, Dataset: June Survey of Agriculture and Horticulture, UK	CSV	08 October 2015	PreviewCSV 'Regional total barley; Areas yields and production', Dataset: June Survey of Agriculture and Horticulture, UK', ...
%    'Regional spring barley; Areas yields and production, Format: CSV, Dataset: June Survey of Agriculture and Horticulture, UK	CSV	08 October 2015	PreviewCSV 'Regional spring barley; Areas yields and production', Dataset: June Survey of Agriculture and Horticulture, UK', ...
%    'Regional winter barley; Areas yields and production, Format: CSV, Dataset: June Survey of Agriculture and Horticulture, UK	CSV	08 October 2015	PreviewCSV 'Regional winter barley; Areas yields and production', Dataset: June Survey of Agriculture and Horticulture, UK', ...
%    'Regional wheat; Areas yields and production, Format: CSV, Dataset: June Survey of Agriculture and Horticulture, UK	CSV	08 October 2015	PreviewCSV 'Regional wheat; Areas yields and production', Dataset: June Survey of Agriculture and Horticulture, UK' ...
%    };
filestems = {...
    'st_osr_18dec14', 'st_roats_18dec14', 'st_rtb_18dec14', ...
    'st_rsb_18dec14', 'st_rwb_18dec14', 'st_rw_18dec14'...
    };
crop_names = {'Oil Seed Rape', 'Oats', 'Total barley', 'Spring barley', 'Winter barley', 'Wheat'};

% Read in one file - wheat for now
ifile = 6;
filename = [datadir,filestems{ifile},'.csv'];
data_table{6} = readtable(filename);
% This ignores the last two lines which read
% ####area = thousand hectares; yield=tonnes per hectare; prodcution =thousands tonnes####
% ####2009 area and production results have been revised to be on a comparable basis with 2010. Yields remain as previously published####
% But it looks like they have labelled their columns wrong - switching
% yield and production! So the production values are actually yields etc.
data_table{6}.Yorkshire_TheHumberYield = data_table{6}.Yorkshire_TheHumberProduction;

ifile = 1;
filename = [datadir,filestems{ifile},'.csv'];
data_table{1} = readtable(filename);
% In this file the yield columns are labelled correctly. But the production
% numbers are coming in as strings - that's probably due to a setting in
% matlab's readtable

ifile = 2;
filename = [datadir,filestems{ifile},'.csv'];
data_table{2} = readtable(filename);
% Hack the yields into the right column - sigh - need to do this properly
data_table{2}.Yorkshire_TheHumberYield = data_table{2}.Yorkshire_TheHumberProduction;

ifile = 3;
filename = [datadir,filestems{ifile},'.csv'];
data_table{3} = readtable(filename)

% For now don't bother about winter vs spring barley
icrops = [1 2 3 6];
ncrop = length(icrops);

% Plot yield vs year for each crop for Yorkshire and Humber 
% Ditto for UK
% Ditto for England

% Make a composite vector of all years covered by the data
years = unique([data_table{1}.year', data_table{2}.year', data_table{3}.year', data_table{6}.year'])';
% remove the NaN entries
years = years(~isnan(years));
nyear = length(years);

% Extract the yield for Yorkshire and Humber from each table
yield_vs_year_crop = zeros(nyear, ncrop);
for jcrop = 1 : ncrop
    icrop = icrops(jcrop);
    for iyear = 1 : nyear
        year = years(iyear);
        irow = find(data_table{icrop}.year == year);
        if (~isempty(irow))
            yield = data_table{icrop}.Yorkshire_TheHumberYield(irow);
            yield_vs_year_crop(iyear, jcrop) = yield;
        end
    end
end

% Plot
clf
plot(years, yield_vs_year_crop)
ylabel('Tonnes per hectare')
xlabel('Year')
legend(crop_names{icrops},'Location','SouthWest')


%