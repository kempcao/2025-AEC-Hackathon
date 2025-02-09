using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.GrasshopperCore;
using AECHackathonZurich_Implenia_GH.Parse;
using AECHackathonZurich_Implenia_GH.Methods;

using Grasshopper.Kernel;

using Newtonsoft.Json;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Components
{
    public class JitterAxesVerticesGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Jitter Axes Vertices";
        private static readonly string _nickname = "JitterAxesVertices";
        private static readonly string _description = "Jitters the panels by randomly shifting their axes' vertices.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Solve;

        public JitterAxesVerticesGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Json Source", "JsonSource", "Source Json file.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Jitter Radius", "JitterRadius", "Maximum jitter distance.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Seed", "Seed", "Jitter seed.", GH_ParamAccess.item, 0);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Json Result", "JsonResult", "Result JSON with snapped vertices.", GH_ParamAccess.item);
            pManager.AddLineParameter("Original Lines", "OriginalLines", "Original wall axes.", GH_ParamAccess.list);
            pManager.AddLineParameter("Jittered Lines", "JitteredLines", "Snapped wall axes", GH_ParamAccess.list);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";
            double jitterDistance = 0.0;
            int seed = 0;

            DA.GetData(0, ref jsonSource);
            DA.GetData(1, ref jitterDistance);
            DA.GetData(2, ref seed);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);

            var originalAxes = Solve.GetPanelsAxes(buildingData);
            var jitteredBuilding = Solve.JitterWallsXY(buildingData, jitterDistance, seed);
            var jitteredAxes = Solve.GetPanelsAxes(jitteredBuilding);
            string jsonResult = JsonConvert.SerializeObject(jitteredBuilding, Formatting.Indented);

            DA.SetData(0, jsonResult);
            DA.SetDataList(1, originalAxes);
            DA.SetDataList(2, jitteredAxes);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("66ca0db9-efab-4e14-8b48-c70462ac8d37"); }
        }
    }
}
