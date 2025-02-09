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
    public class MoveBackToOriginalOrientationGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Move Back To Original Orientation";
        private static readonly string _nickname = "MoveBackToOriginalOrientation";
        private static readonly string _description = "Move back to the original orientation.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Solve;

        public MoveBackToOriginalOrientationGH()
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
            pManager.AddTransformParameter("Applied Transform", "AppliedTransform", "What transform was applied to get back to the original.", GH_ParamAccess.item);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";

            DA.GetData(0, ref jsonSource);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);

            var movedBack = Solve.TransformBack(buildingData, out Transform appliedTransform);
            var jsonResult = JsonConvert.SerializeObject(movedBack, Formatting.Indented);

            DA.SetData(0, jsonResult);
            DA.SetData(1, appliedTransform);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("d0949d7a-ae2c-4d0c-bc14-6d96dd86d8a6"); }
        }
    }
}
