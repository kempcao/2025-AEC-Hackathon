using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Threading.Tasks;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Comparers
{
    public struct LabeledPoint
    {
        public string Label { get; set; }
        public Point3d Position { get; set; }

        public LabeledPoint(Point3d position, string label)
        {
            this.Position = position;
            this.Label = label;
        }
    }
}
