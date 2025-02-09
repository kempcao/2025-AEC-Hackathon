using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using AECHackathonZurich_Implenia_GH.Data;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Methods
{
    public static partial class Solve
    {
        public static Box FindSmallestBoundingBox(BuildingData buildingData, out Vector3d targetYAxis, out Transform alignmentTransform)
        {
            var allVertices = GetPanelsAxes(buildingData).SelectMany(x => new List<Point3d>{ x.From, x.To }).ToList();
            allVertices.AddRange(GetSpacesOutlines(buildingData, out _).SelectMany(x => x.ToList()));

            return FindSmallestBoundingBox(allVertices, out targetYAxis, out alignmentTransform);
        }

        public static Box FindSmallestBoundingBox(List<Point3d> vertices, out Vector3d targetYAxis, out Transform alignmentTransform)
        {
            Plane basePlane = Plane.WorldXY;
            Grasshopper.Kernel.Geometry.Node2List node2List = new Grasshopper.Kernel.Geometry.Node2List();
            List<Point3d> projectedVertices = new List<Point3d>();

            foreach (Point3d pt in vertices) {
                pt.Transform(Transform.PlanarProjection(basePlane));
                projectedVertices.Add(pt);
                double u, v;
                basePlane.ClosestParameter(pt, out u, out v);
                node2List.Append(new Grasshopper.Kernel.Geometry.Node2(u, v));
            }

            List<int> hullIndices = new List<int>();
            if (!Grasshopper.Kernel.Geometry.ConvexHull.Solver.Compute(node2List, hullIndices)) {
                targetYAxis = Vector3d.YAxis;
                alignmentTransform = Transform.Identity;
                return new Box(Plane.WorldXY, projectedVertices);
            }

            Polyline hull = new Polyline();
            for (int i = 0; i < hullIndices.Count; i++) {
                hull.Add(projectedVertices[hullIndices[i]]);
            }
            if (hull.Count > 1) {
                hull.Add(hull[0]);
            }

            hull.DeleteShortSegments(0.001);
            Line[] segments = hull.GetSegments();
            Vector3d[] directions = new Vector3d[segments.Length];
            for (int i = 0; i < segments.Length; i++) {
                directions[i] = segments[i].Direction;
                directions[i].Unitize();
            }

            double minArea = double.PositiveInfinity;
            Box minBox = new Box(Plane.WorldXY, vertices);
            targetYAxis = Vector3d.YAxis;

            for (int i = 0; i < directions.Length; i++) {
                Vector3d yAxis = Vector3d.CrossProduct(basePlane.ZAxis, directions[i]);
                Box curBox = new Box(new Plane(basePlane.Origin, directions[i], yAxis), vertices);
                double area = curBox.Area;
                if (area < minArea) {
                    minArea = area;
                    minBox = curBox;
                    targetYAxis = yAxis;
                }
            }

            Vector3d translationVector = (Vector3d)minBox.PointAt(0, 0, 0) * -1;
            double angleRad = Vector3d.VectorAngle(targetYAxis, Vector3d.YAxis);
            alignmentTransform = Transform.Rotation(angleRad, Point3d.Origin) * Transform.Translation(translationVector);

            return minBox;
        }
    }
}
