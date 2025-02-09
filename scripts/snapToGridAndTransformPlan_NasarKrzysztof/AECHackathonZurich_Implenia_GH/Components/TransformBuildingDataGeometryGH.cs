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
    public class TransformBuildingDataGeometryGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Transform Building Data";
        private static readonly string _nickname = "TransformBuildingData";
        private static readonly string _description = "Transforms the building data geometry and updates the stored transform matrix.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Solve;

        public TransformBuildingDataGeometryGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Json Source", "JsonSource", "Source Json file.", GH_ParamAccess.item);
            pManager.AddTransformParameter("Transform", "Transform", "Transform matrix", GH_ParamAccess.item);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Json Result", "JsonResult", "Result JSON with snapped vertices.", GH_ParamAccess.item);
            pManager.AddTransformParameter("Combined Transforms", "CombinedTransforms", "All transforms from the original.", GH_ParamAccess.item);
            pManager.AddTransformParameter("Transform To Original", "TransformToOriginal", "Transform to get back to the original orientation.", GH_ParamAccess.item);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";
            Transform xForm = new Transform();

            DA.GetData(0, ref jsonSource);
            DA.GetData(1, ref xForm);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);
            var transformedBuildingData = Solve.TransformBuildingDataGeometry(buildingData, xForm);
            string jsonResult = JsonConvert.SerializeObject(transformedBuildingData, Formatting.Indented);

            DA.SetData(0, jsonResult);
            DA.SetData(1, transformedBuildingData.GetAppliedTransformMatrix());
            DA.SetData(2, transformedBuildingData.GetTransformMatrixToTheOriginal());
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("7290c340-7fee-4373-8b8c-60aefb56aa28"); }
        }
    }
}
