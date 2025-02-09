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
    public class GetAxesFromJsonGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Get Axes From Json";
        private static readonly string _nickname = "GetAxesFromJson";
        private static readonly string _description = "Get axes geometry from Json.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Get;

        public GetAxesFromJsonGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Json Source", "JsonSource", "Source Json file.", GH_ParamAccess.item);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddLineParameter("Panels", "Panels", "Panels.", GH_ParamAccess.list);
            pManager.AddCurveParameter("Spaces", "Spaces", "Spaces.", GH_ParamAccess.list);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";

            DA.GetData(0, ref jsonSource);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);

            var panelsAxes = Solve.GetPanelsAxes(buildingData);
            var spaceOutlines = Solve.GetSpacesOutlines(buildingData, out _);

            DA.SetDataList(0, panelsAxes);
            DA.SetDataList(1, spaceOutlines);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("9d1cd88d-9668-4b98-9371-ff52e1da5931"); }
        }
    }
}
