using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


using Eto.Drawing;

using Rhino.Geometry;

namespace AECHackathonZurich_Implenia_GH.Methods
{
    #region
    // A simple helper “labeled polyline” class.
    public class LabeledPolyline
    {
        public string Label;
        public Polyline Poly;

        public LabeledPolyline(string label, Polyline poly)
        {
            Label = label;
            Poly = poly;
        }

        /// <summary>
        /// Computes a “center” for the polyline by averaging the mid–points of its segments.
        /// </summary>
        public Point3d Center()
        {
            if (Poly.Count < 2)
                return Poly[0];

            Point3d sum = Point3d.Origin;
            int segCount = Poly.Count - 1; // works for open or closed (if closed, last point = first)
            for (int i = 0; i < segCount; i++) {
                Point3d mid = (Poly[i] + Poly[i + 1]) / 2.0;
                sum += (Vector3d)mid;
            }
            return new Point3d(sum.X / segCount, sum.Y / segCount, sum.Z / segCount);
        }

        /// <summary>
        /// Returns the vertices of the polyline.
        /// </summary>
        public List<Point3d> Vertices()
        {
            return new List<Point3d>(Poly);
        }
    }
    #endregion

    public class SpaceMatching
    {
        /* 
          INPUTS (set these up as inputs on the C# component):
             List<LabeledPolyline> sourcePolylines
             List<LabeledPolyline> targetPolylines

          OUTPUTS (set these up as outputs):
             object MatchedPolylines   // A list of matching data – see below.
        */

        /*
          The following algorithm does:

          1. For each source polyline, it collects the target polylines with the same label.
             Then it computes the center of the source polyline and the centers of each candidate target polyline.
             It picks the target whose center is closest.

          2. For each source-target pair, it “matches” the vertices.
             If there are at least as many target vertices as source vertices, then a one-to-one (injective) 
             assignment is computed by checking all permutations (suitable for small numbers).
             Otherwise, for each source vertex the target vertex that is closest is assigned.

          (The code uses a brute-force “permutation” approach for the one-to-one assignment.
           In a production solution you might replace this with a proper Hungarian algorithm.)
        */

        // MAIN METHOD:
        public List<Tuple<LabeledPolyline, LabeledPolyline, List<Tuple<Point3d, Point3d>>>> MatchPolylines(
            List<LabeledPolyline> sourcePolylines,
            List<LabeledPolyline> targetPolylines)
        {
            // The output is a list of tuples.
            var output = new List<Tuple<LabeledPolyline, LabeledPolyline, List<Tuple<Point3d, Point3d>>>>();

            // Process each source polyline.
            foreach (var src in sourcePolylines) {
                // 1. Filter target polylines by matching label.
                var sameLabelTargets = targetPolylines.Where(t => t.Label == src.Label).ToList();
                if (sameLabelTargets.Count == 0)
                    continue;

                // 2. Pick the target polyline whose center is closest to the source polyline’s center.
                LabeledPolyline bestTgt = PickTargetByCenter(src, sameLabelTargets);

                // 3. Determine the best pairing between vertices.
                var pairing = BestVertexPairing(src.Vertices(), bestTgt.Vertices());

                // 4. Store the result.
                output.Add(new Tuple<LabeledPolyline, LabeledPolyline, List<Tuple<Point3d, Point3d>>>(src, bestTgt, pairing));
            }

            return output;
        }
        /// <summary>
        /// Given a source polyline and a list of target polylines (with matching labels),
        /// pick the one whose center is closest to the source center.
        /// </summary>
        LabeledPolyline PickTargetByCenter(LabeledPolyline source, List<LabeledPolyline> candidates)
        {
            double bestDist = double.MaxValue;
            LabeledPolyline best = null;
            Point3d srcCenter = source.Center();
            foreach (var t in candidates) {
                double d = srcCenter.DistanceTo(t.Center());
                if (d < bestDist) {
                    bestDist = d;
                    best = t;
                }
            }
            return best;
        }

        /// <summary>
        /// Given two lists of vertices, return a pairing (as a list of tuples)
        /// that minimizes the total distance between source and target vertices.
        /// If there are at least as many target vertices as source vertices, the pairing
        /// will be one-to-one. Otherwise, each source vertex is assigned its nearest target vertex.
        /// </summary>
        List<Tuple<Point3d, Point3d>> BestVertexPairing(List<Point3d> source, List<Point3d> target)
        {
            if (target.Count >= source.Count)
                return AssignVerticesOneToOne(source, target);
            else
                return AssignVerticesAllowDuplicates(source, target);
        }

        /// <summary>
        /// For each source vertex, find the nearest target vertex (allowing duplicates).
        /// </summary>
        List<Tuple<Point3d, Point3d>> AssignVerticesAllowDuplicates(List<Point3d> source, List<Point3d> target)
        {
            List<Tuple<Point3d, Point3d>> pairs = new List<Tuple<Point3d, Point3d>>();
            foreach (var s in source) {
                double best = double.MaxValue;
                Point3d bestTarget = Point3d.Unset;
                foreach (var t in target) {
                    double d = s.DistanceTo(t);
                    if (d < best) {
                        best = d;
                        bestTarget = t;
                    }
                }
                pairs.Add(Tuple.Create(s, bestTarget));
            }
            return pairs;
        }

        /// <summary>
        /// When target vertices are numerous enough, search for the one-to-one assignment that minimizes the sum of distances.
        /// Here we use a brute-force permutation (suitable only when source.Count is small).
        /// </summary>
        List<Tuple<Point3d, Point3d>> AssignVerticesOneToOne(List<Point3d> source, List<Point3d> target)
        {
            List<Tuple<Point3d, Point3d>> bestPairs = null;
            double bestCost = double.MaxValue;
            // We need to choose a distinct target vertex for each source vertex.
            // Build a list of candidate target indices.
            List<int> allIndices = Enumerable.Range(0, target.Count).ToList();
            // Get all permutations of length source.Count.
            foreach (var perm in Permutations(allIndices, source.Count)) {
                double cost = 0;
                for (int i = 0; i < source.Count; i++)
                    cost += source[i].DistanceTo(target[perm[i]]);
                if (cost < bestCost) {
                    bestCost = cost;
                    bestPairs = new List<Tuple<Point3d, Point3d>>();
                    for (int i = 0; i < source.Count; i++)
                        bestPairs.Add(Tuple.Create(source[i], target[perm[i]]));
                }
            }
            return bestPairs;
        }

        /// <summary>
        /// Generates all permutations of length 'length' from the list 'list'
        /// (without repeating any element).
        /// </summary>
        IEnumerable<List<int>> Permutations(List<int> list, int length)
        {
            if (length == 1)
                return list.Select(t => new List<int> { t });

            return Permutations(list, length - 1)
                   .SelectMany(t => list.Where(e => !t.Contains(e)),
                               (t, e) =>
                               {
                                   var nt = new List<int>(t);
                                   nt.Add(e);
                                   return nt;
                               });
        }

    }
}
