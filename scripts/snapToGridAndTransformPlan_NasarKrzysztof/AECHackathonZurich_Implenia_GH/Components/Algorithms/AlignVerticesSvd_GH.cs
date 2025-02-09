using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Comparers;
using AECHackathonZurich_Implenia_GH.GrasshopperCore;
using AECHackathonZurich_Implenia_GH.Methods;
using AECHackathonZurich_Implenia_GH.Parse;
using Grasshopper.Kernel;
using Newtonsoft.Json;
using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Components.Algorithms
{
    public class AlignVerticesSvd_GH : AECHackathonGH_Component
    {
        private static readonly string _name = "Align Vertices SVD";
        private static readonly string _nickname = "AlignVerticesSVD";
        private static readonly string _description = "Find the best alignment with singular value decomposition.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Algorithms;

        public AlignVerticesSvd_GH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddPointParameter("Vertices", "Vertices", "Vertices to align.", GH_ParamAccess.list);
            pManager.AddPointParameter("Target Vertices", "TargetVertices", "Vertices to align to.", GH_ParamAccess.list);
            pManager.AddIntegerParameter("Max Iterations", "MaxIterations", "Maximum number of iterations", GH_ParamAccess.item, 10);
            pManager.AddNumberParameter("Tolerance", "Tolerance", "Tolerance", GH_ParamAccess.item, 0.00001);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTransformParameter("Best Alignment Transform", "BestAlignmentTransform", "Transform that will result in the best alignment", GH_ParamAccess.item);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            var pointList = new List<Point3d>();
            var targetPointList = new List<Point3d>();
            int maxIter = 10;
            double tolerance = 0.0001;

            DA.GetDataList(0, pointList);
            DA.GetDataList(1, targetPointList);
            DA.GetData(2, ref maxIter);
            DA.GetData(3, ref  tolerance);

            IcpSolver solver = new IcpSolver(pointList.ToArray(), targetPointList.ToArray());
            var transform = solver.Solve(maxIter, tolerance);

            DA.SetData(0, transform);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("7e39401d-6f83-4dfa-bd80-f5e4779c7bb5"); }
        }
    }
}
