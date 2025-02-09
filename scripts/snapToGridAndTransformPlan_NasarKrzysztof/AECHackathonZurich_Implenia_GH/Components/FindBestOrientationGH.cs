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
    public class FindBestOrientationGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Find Best Orientation";
        private static readonly string _nickname = "FindBestOrientation";
        private static readonly string _description = "Find the best orientation of the plan.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Solve;

        public FindBestOrientationGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Json Source", "JsonSource", "Source Json file.", GH_ParamAccess.item);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Json Result", "JsonResult", "Result JSON with snapped vertices.", GH_ParamAccess.item);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";

            DA.GetData(0, ref jsonSource);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);

            var smallestBox = Solve.FindSmallestBoundingBox(buildingData, out Vector3d newY, out Transform alignmentTransform);
            var alignedBuildingData = Solve.TransformBuildingDataGeometry(buildingData, alignmentTransform);
            var jsonResult = JsonConvert.SerializeObject(alignedBuildingData, Formatting.Indented);

            DA.SetData(0, jsonResult);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("a18f3945-16b2-45bb-aa2e-06d99cffcc00"); }
        }
    }
}
