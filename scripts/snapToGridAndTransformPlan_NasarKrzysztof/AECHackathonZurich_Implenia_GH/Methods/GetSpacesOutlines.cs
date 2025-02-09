using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Data;
using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Methods
{
    public static partial class Solve
    {
        public static List<Polyline> GetSpacesOutlines(BuildingData buildingData, out List<string> labels)
        {
            List<Polyline> spacesOutlines = new List<Polyline>();
            labels = new List<string>();

            foreach (var space in buildingData.Spaces) {
                spacesOutlines.Add(space.Value.ToPolyline());
                labels.Add(space.Value.RoomType.ToString());
            }

            return spacesOutlines;
        }
    }
}
