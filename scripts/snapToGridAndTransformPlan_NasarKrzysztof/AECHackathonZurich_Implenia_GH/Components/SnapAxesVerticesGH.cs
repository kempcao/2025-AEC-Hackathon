using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.GrasshopperCore;
using AECHackathonZurich_Implenia_GH.Methods;
using AECHackathonZurich_Implenia_GH.Parse;

using Grasshopper.Kernel;
using Newtonsoft.Json;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Components
{
    public class SnapAxesVerticesGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Snap Axes Vertices";
        private static readonly string _nickname = "SnapAxesVertices";
        private static readonly string _description = "Cleans the wall axes model by snapping the vertices to the grid. Works only for orthogonal plans.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Solve;

        public SnapAxesVerticesGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Json Source", "JsonSource", "Source Json file.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Snapping Threshold", "SnappingThreshold", "Maximum distance within which the points are considered coincident.", GH_ParamAccess.item);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Json Result", "JsonResult", "Result JSON with snapped vertices.", GH_ParamAccess.item);
            pManager.AddLineParameter("Original Lines", "OriginalLines", "Original wall axes.", GH_ParamAccess.list);
            pManager.AddLineParameter("Snapped Lines", "SnappedLines", "Snapped wall axes", GH_ParamAccess.list);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";
            double threshold = 0.0;

            DA.GetData(0, ref jsonSource);
            DA.GetData(1, ref threshold);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);

            List<Line> panelsAxes = Solve.GetPanelsAxes(buildingData);
            var snappedBuilding = Solve.SnapWallsAxes(buildingData, threshold);
            List<Line> snappedAxes = Solve.GetPanelsAxes(snappedBuilding);
            string jsonResult = JsonConvert.SerializeObject(snappedBuilding, Formatting.Indented);

            DA.SetData(0, jsonResult);
            DA.SetDataList(1, panelsAxes);
            DA.SetDataList(2, snappedAxes);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("a3de43fe-dcdd-4b77-baf5-81a45509de53"); }
        }
    }
}
