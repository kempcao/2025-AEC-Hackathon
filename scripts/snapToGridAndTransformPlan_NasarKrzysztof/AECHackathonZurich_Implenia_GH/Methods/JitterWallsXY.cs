using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Data;

using Eto.Forms;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Methods
{
    public static partial class Solve
    {
        public static BuildingData JitterWallsXY(BuildingData sourceBuilding, double jitterRadius, int seed)
        {
            Random random = new Random(seed);

            var jitteredBuilding = sourceBuilding.DeepCopy();

            foreach (var panel in sourceBuilding.Panels.Items) {
                jitteredBuilding.Panels.Items[panel.Key].StartPoint[0] = JitterValue(panel.Value.StartPoint[0], jitterRadius, random);
                jitteredBuilding.Panels.Items[panel.Key].StartPoint[1] = JitterValue(panel.Value.StartPoint[1], jitterRadius, random);
                jitteredBuilding.Panels.Items[panel.Key].EndPoint[0] = JitterValue(panel.Value.EndPoint[0], jitterRadius, random);
                jitteredBuilding.Panels.Items[panel.Key].EndPoint[1] = JitterValue(panel.Value.EndPoint[1], jitterRadius, random);
            }

            foreach (var space in sourceBuilding.Spaces) {
                int i = 0;
                foreach (var coordinate in space.Value.Coordinates) {
                    jitteredBuilding.Spaces[space.Key].Coordinates[i].X = JitterValue(coordinate.X, jitterRadius, random);
                    jitteredBuilding.Spaces[space.Key].Coordinates[i].Y = JitterValue(coordinate.Y, jitterRadius, random);
                    i++;
                }
            }
            return jitteredBuilding;
        }

        private static double JitterValue(double x, double radius, Random rng)
        {
            double jitter = (rng.NextDouble() - 0.5) * 2 * radius;
            return jitter + x;
        }
    }
}
