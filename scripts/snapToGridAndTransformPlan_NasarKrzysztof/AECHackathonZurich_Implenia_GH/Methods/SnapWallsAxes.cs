using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Data;

using Eto.Forms;

using Rhino.Geometry;
using Rhino.UI;

namespace AECHackathonZurich_Implenia_GH.Methods
{
    public static partial class Solve
    {
        public static BuildingData SnapWallsAxes(BuildingData sourceBuildingData, double threshold) {
            var xCoordinates = new List<MultiCoordinate>();
            var yCoordinates = new List<MultiCoordinate>();

            foreach (var panel in sourceBuildingData.Panels.Items) {
                double xStart = panel.Value.StartPoint[0];
                double yStart = panel.Value.StartPoint[1];
                double xEnd = panel.Value.EndPoint[0];
                double yEnd = panel.Value.EndPoint[1];

                xCoordinates.Add(new MultiCoordinate(panel.Key + "s", xStart));
                xCoordinates.Add(new MultiCoordinate(panel.Key + "e", xEnd));
                yCoordinates.Add(new MultiCoordinate(panel.Key + "s", yStart));
                yCoordinates.Add(new MultiCoordinate(panel.Key + "e", yEnd));
            }
            foreach (var space in sourceBuildingData.Spaces) {
                int i = 0;
                foreach (var coordinate in space.Value.Coordinates) {
                    double x = coordinate.X;
                    double y = coordinate.Y;

                    xCoordinates.Add(new MultiCoordinate(space.Key + "_" + i + "a", x));
                    yCoordinates.Add(new MultiCoordinate(space.Key + "_" + i + "a", y));
                    i++;
                }
            }

            xCoordinates = xCoordinates.OrderBy(x => x.Values[0]).ToList();
            yCoordinates = yCoordinates.OrderBy(y => y.Values[0]).ToList();

            var xCoordinatesGroups = new List<MultiCoordinate>();
            var yCoordinatesGroups = new List<MultiCoordinate>();

            var currentXGroup = xCoordinates[0];
            for (int i = 1; i < xCoordinates.Count; i++) {
                if (currentXGroup.FitsInGroup(xCoordinates[i].Values[0], threshold)) {
                    currentXGroup.MergeIn(xCoordinates[i]);
                }
                else {
                    xCoordinatesGroups.Add(currentXGroup);
                    currentXGroup = new MultiCoordinate(xCoordinates[i].Sources[0], xCoordinates[i].Values[0]);
                }
            }
            xCoordinatesGroups.Add(currentXGroup);

            var currentYGroup = yCoordinates[0];
            for (int i = 1; i < yCoordinates.Count; i++) {
                if (currentYGroup.FitsInGroup(yCoordinates[i].Values[0], threshold)) {
                    currentYGroup.MergeIn(yCoordinates[i]);
                }
                else {
                    yCoordinatesGroups.Add(currentYGroup);
                    currentYGroup = new MultiCoordinate(yCoordinates[i].Sources[0], yCoordinates[i].Values[0]);
                }
            }
            yCoordinatesGroups.Add(currentYGroup);

            var alteredBuildingData = sourceBuildingData.DeepCopy();

            foreach (var xCoordinateGroup in xCoordinatesGroups) {
                double snapValue = xCoordinateGroup.GetMedian();
                foreach (var source in xCoordinateGroup.Sources) {
                    if (source.EndsWith("a")) { // is space 
                        string[] spaceId = source.Substring(0, source.Length - 1).Split('_');
                        alteredBuildingData.Spaces[spaceId[0]].Coordinates[int.Parse(spaceId[1])].X = snapValue;
                    }
                    else {
                        string panelId = source.Substring(0, source.Length - 1);
                        bool isStart = source.EndsWith("s");
                        if (isStart) {
                            alteredBuildingData.Panels.Items[panelId].StartPoint[0] = snapValue;
                        }
                        else {
                            alteredBuildingData.Panels.Items[panelId].EndPoint[0] = snapValue;
                        }
                    }
                }
            }

            foreach (var yCoordinateGroup in yCoordinatesGroups) {
                double snapValue = yCoordinateGroup.GetMedian();
                foreach (var source in yCoordinateGroup.Sources) {
                    if (source.EndsWith("a")) { // is space 
                        string[] spaceId = source.Substring(0, source.Length - 1).Split('_');
                        alteredBuildingData.Spaces[spaceId[0]].Coordinates[int.Parse(spaceId[1])].Y = snapValue;
                    }
                    else {
                        string panelId = source.Substring(0, source.Length - 1);
                        bool isStart = source.EndsWith("s");
                        if (isStart) {
                            alteredBuildingData.Panels.Items[panelId].StartPoint[1] = snapValue;
                        }
                        else {
                            alteredBuildingData.Panels.Items[panelId].EndPoint[1] = snapValue;
                        }
                    }
                }
            }

            return alteredBuildingData;
        }

        internal class MultiCoordinate
        {
            public List<double> Values { get; set; } = new List<double>();
            public List<string> Sources {  get; set; } = new List<string> ();
            public double GetMedian()
            {
                var numbers = Values.ToList();
                int count = numbers.Count;
                int middleIndex = count / 2;

                if (count % 2 == 0) {
                    return (numbers[middleIndex - 1] + numbers[middleIndex]) / 2.0;
                }
                else {
                    return numbers[middleIndex];
                }
            }

            public MultiCoordinate(string source, double value)
            {
                Sources = new List<string>() { source };
                Values = new List<double>() { value };                
            }

            public bool FitsInGroup(double value, double threshold)
            {
                return Values.Any(x => Math.Abs(x - value) <= threshold);
            }

            public void MergeIn(MultiCoordinate other)
            {
                Values.AddRange(other.Values);
                Sources.AddRange(other.Sources);
            }
        }
    }
}
