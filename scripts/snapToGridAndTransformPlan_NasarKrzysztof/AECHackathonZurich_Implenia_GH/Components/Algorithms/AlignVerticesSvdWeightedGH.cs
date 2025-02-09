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
    public class AlignVerticesSvdWeighted_GH : AECHackathonGH_Component
    {
		private static readonly string _name = "Align Vertices SVD Weighted";
		private static readonly string _nickname = "AlignVerticesSVDWeighted";
		private static readonly string _description = "Find the best alignment with singular value decomposition, where transforms are computed for groups denoted by labels and weights proportional to the groups' sizes.";
		private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Algorithms;

        public AlignVerticesSvdWeighted_GH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddPointParameter("Vertices", "Vertices", "Vertices to align.", GH_ParamAccess.list);
            pManager.AddTextParameter("Labels", "Labels", "Labels for vertices to align.", GH_ParamAccess.list);
            pManager.AddPointParameter("Target Vertices", "TargetVertices", "Vertices to align to.", GH_ParamAccess.list);
            pManager.AddTextParameter("Target Labels", "TargetLabel", "Labels for target vertices.", GH_ParamAccess.list);
            pManager.AddIntegerParameter("Main Iterations", "MainIterations", "Maximum number of main iterations", GH_ParamAccess.item, 10);
			pManager.AddIntegerParameter("Interim Iterations", "InterimIterations", "Maximum number of intermin iterations (when computing individual groups' transforms).", GH_ParamAccess.item, 1);
			pManager.AddNumberParameter("Tolerance", "Tolerance", "Tolerance", GH_ParamAccess.item, 0.00001);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTransformParameter("Best Alignment Transform", "BestAlignmentTransform", "Transform that will result in the best alignment", GH_ParamAccess.item);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            var pointList = new List<Point3d>();
            var labelList = new List<string>();
            var targetPointList = new List<Point3d>();
            var targetLabelList = new List<string>();
            int maxIter = 10;
            int interimIter = 1;
            double tolerance = 0.0001;

            DA.GetDataList(0, pointList);
            DA.GetDataList(1, labelList);
            DA.GetDataList(2, targetPointList);
            DA.GetDataList(3, targetLabelList);
            DA.GetData(4, ref maxIter);
			DA.GetData(5, ref interimIter);
			DA.GetData(6, ref tolerance);

            var sourcePts = pointList.Zip(labelList, (pt, label) => new LabeledPoint(pt, label)).ToList();
            var targetPts = targetPointList.Zip(targetLabelList, (pt, label) => new LabeledPoint(pt, label)).ToList();

            Transform transform = Transform.Identity;

            for (int i = 0; i < maxIter; i++) {
                Transform nextStep = WeightedSVDAlignment.AlignPointsWeighted(sourcePts, targetPts, interimIter);
                for (int j = 0; j < sourcePts.Count; j++) {
                    Point3d curPosition = sourcePts[j].Position;
                    curPosition.Transform(nextStep);
                    sourcePts[j] = new LabeledPoint(curPosition, sourcePts[j].Label);
                }
                transform = nextStep * transform;
            }

            DA.SetData(0, transform);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("b227b531-25e9-4bc2-9bfb-ff5bc6ae0d7f"); }
        }
    }
}
