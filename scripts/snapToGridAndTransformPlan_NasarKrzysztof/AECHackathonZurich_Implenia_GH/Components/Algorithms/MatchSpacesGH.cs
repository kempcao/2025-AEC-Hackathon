using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.GrasshopperCore;
using AECHackathonZurich_Implenia_GH.Methods;
using AECHackathonZurich_Implenia_GH.Parse;

using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;

using Rhino.DocObjects;
using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Components.Algorithms
{
    public class MatchSpacesGH : AECHackathonGH_Component
    {
        private static readonly string _name = "Match Spaces";
        private static readonly string _nickname = "MatchSpaces";
        private static readonly string _description = "Match spaces for similarity comparison.";
        private static readonly AECHackathonGH_Info.Group _group = AECHackathonGH_Info.Group.Algorithms;

        public MatchSpacesGH()
            : base(_name, _nickname, _description, _group)
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddCurveParameter("Spaces Source", "SpacesSource", "Spaces.", GH_ParamAccess.list);
            pManager.AddTextParameter("Labels Source", "LabelsSource", "Labels.", GH_ParamAccess.list);
            pManager.AddCurveParameter("Spaces Target", "SpacesTarget", "Spaces.", GH_ParamAccess.list);
            pManager.AddTextParameter("Labels Target", "LabelsTarget", "Labels.", GH_ParamAccess.list);
        }
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddCurveParameter("SpacesA", "SpacesA", "Spaces.", GH_ParamAccess.list);
            pManager.AddCurveParameter("SpacesB", "SpacesB", "Spaces.", GH_ParamAccess.list);
            pManager.AddLineParameter("Point Pairs", "PointPairs", "PointPairs.", GH_ParamAccess.tree);
        }
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            List<Curve> sourceCurves = new List<Curve>();
            List<string> sourceLabels = new List<string>();
            List<Curve> targetCurves = new List<Curve>();
            List<string> targetLabels = new List<string>();

            DA.GetDataList(0, sourceCurves);
            DA.GetDataList(1, sourceLabels);
            DA.GetDataList(2, targetCurves);
            DA.GetDataList(3, targetLabels);

            List<Polyline> sourcePolylines = new List<Polyline>();
            List<Polyline> targetPolylines = new List<Polyline>();

            foreach (Curve curve in sourceCurves) {
                curve.TryGetPolyline(out Polyline poly);
                sourcePolylines.Add(poly);
            }
            foreach (Curve curve in targetCurves) {
                curve.TryGetPolyline(out Polyline poly);
                targetPolylines.Add(poly);
            }

            SpaceMatching solver = new SpaceMatching();
            var labeledSource = sourcePolylines.Zip(sourceLabels, (poly, label) => new LabeledPolyline(label, poly)).ToList();
            var labeledTarget = targetPolylines.Zip(targetLabels, (poly, label) => new LabeledPolyline(label, poly)).ToList();

            var result = solver.MatchPolylines(labeledSource, labeledTarget);

            List<Polyline> resultSpacesA = new List<Polyline>();
            List<Polyline> resultSpacesB = new List<Polyline>();
            DataTree<Line> vertexConnections = new DataTree<Line>();

            for (int i = 0; i < result.Count; i++) {
                GH_Path pth = new GH_Path(i);
                vertexConnections.EnsurePath(pth);
                resultSpacesA.Add(result[i].Item1.Poly);
                resultSpacesB.Add(result[i].Item2.Poly);
                foreach (var pointPair in result[i].Item3) {
                    vertexConnections.Add(new Line(pointPair.Item1, pointPair.Item2), pth);
                }
            }

            DA.SetDataList(0, resultSpacesA);
            DA.SetDataList(1, resultSpacesB);
            DA.SetDataTree(2, vertexConnections);
        }

        public override GH_Exposure Exposure {
            get { return GH_Exposure.primary; }
        }

        public override Guid ComponentGuid {
            get { return new Guid("1ab15857-390d-4f1b-a012-656666bbd685"); }
        }
    }
}
