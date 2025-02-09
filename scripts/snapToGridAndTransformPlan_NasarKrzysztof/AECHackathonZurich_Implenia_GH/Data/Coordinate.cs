using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using Newtonsoft.Json;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Data
{
    public class Coordinate
    {
        [JsonProperty("x")]
        public double X { get; set; }

        [JsonProperty("y")]
        public double Y { get; set; }

        [JsonProperty("z")]
        public double Z { get; set; }

        public Coordinate(Point3d point)
        {
            X = point.X;
            Y = point.Y;
            Z = point.Z;
        }
    }
}
