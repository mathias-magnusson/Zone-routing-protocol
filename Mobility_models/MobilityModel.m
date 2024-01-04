format shortG           % better number formatting.

% Create satellite constellation
startTime = datetime(2023, 9, 11, 9,00,00, Timezone = 'Europe/Copenhagen');
periodTime = 100;
stopTime =  startTime + minutes(periodTime);
sampleTime = 30;            % Seconds
sc = satelliteScenario(startTime, stopTime, sampleTime, AutoSimulate = false);

earthRadius = 6378137;                                                   % meters
altitude = 718000;                                                       % meters

sat = walkerStar(sc, (earthRadius+altitude), 86.4, 66, 6, 2, Name="Sat", OrbitPropagator="sgp4");

numSat = numel(sat);
gsSource = groundStation(sc, 56.09, 10.12, Name="Aarhus");
gsTarget = groundStation(sc, -28.02, 153.4, Name="Gold Coast");

%%
satelliteScenarioViewer(sc);
%%
counter = 1;
mobilityModel = zeros(sampleTime,numSat,3);

while sc.SimulationTime < stopTime
    advance(sc);
    sc.SimulationTime;
    [pos,vel] = states(sat, sc.SimulationTime, c = 'ecef');
    pos = reshape(pos,3,numSat)';

    mobilityModel(counter,:,:) = pos;
    counter = counter + 1;
end

%% Write to data.csv file 

fid = fopen('Mobility_models/walkerStar/walkerStar_66_100_min_200_samples_718.csv', 'a+');

for n = 1:periodTime*(60/sampleTime)
    for i = 1:numSat
        fprintf(fid, '%.6f %.6f %.6f', mobilityModel(n,i,1:3));
        if i < numSat
            fprintf(fid, ',');
        end
    end
    fprintf(fid, '\n');
end

fclose(fid);

%% Checking whether the nodes have access to each other

sc.AutoSimulate = true;
%nodes = {sat(1) sat(11) sat(10) sat(58) sat(48) sat(49)};
nodes = {sat(1) sat(49)};
ac = access(nodes{:});
ac.LineColor = "red";
intvls = accessIntervals(ac)

satelliteScenarioViewer(sc, ShowDetails=false);








