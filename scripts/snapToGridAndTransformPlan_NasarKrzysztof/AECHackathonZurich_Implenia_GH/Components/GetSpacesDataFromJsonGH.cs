using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.GrasshopperCore;
using AECHackathonZurich_Implenia_GH.Methods;
using AECHackathonZurich_Implenia_GH.Parse;
using Grasshopper.Kernel;

namespace AECHackathonZurich_Implenia_GH.Components
{
    public class GetSpacesDataFromJsonGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Get Spaces Data From Json";
        private static readonly string _nickname = "GetSpacesDataFromJson";
        private static readonly string _description = "Get spaces outlines and labels.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Get;

        public GetSpacesDataFromJsonGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Json Source", "JsonSource", "Source Json file.", GH_ParamAccess.item);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddCurveParameter("Spaces", "Spaces", "Spaces.", GH_ParamAccess.list);
            pManager.AddTextParameter("Labels", "Labels", "Labels.", GH_ParamAccess.list);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string jsonSource = "";

            DA.GetData(0, ref jsonSource);

            var buildingData = BuildingDataFromJson.Parse(jsonSource);

            var spaceOutlines = Solve.GetSpacesOutlines(buildingData, out List<string> labels);

            DA.SetDataList(0, spaceOutlines);
            DA.SetDataList(1, labels);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("5bb40234-6334-4ec6-831a-6dab599e2a57"); }
        }
    }
}
