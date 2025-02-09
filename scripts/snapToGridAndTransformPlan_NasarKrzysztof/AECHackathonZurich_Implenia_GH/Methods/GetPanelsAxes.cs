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
        public static List<Line> GetPanelsAxes(BuildingData buildingData)
        {
            List<Line> panelsAxes = new List<Line>();

            foreach (var panel in buildingData.Panels.Items) {                
                panelsAxes.Add(panel.Value.ToLine());
            }

            return panelsAxes;
        }
    }
}
