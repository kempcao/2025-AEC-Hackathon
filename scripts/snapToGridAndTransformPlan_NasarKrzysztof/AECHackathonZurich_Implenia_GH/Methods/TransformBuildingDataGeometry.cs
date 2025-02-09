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
        public static BuildingData TransformBuildingDataGeometry(BuildingData sourceBuilding, Rhino.Geometry.Transform transformMatrix)
        {
            var transformedBuilding = sourceBuilding.DeepCopy();

            foreach (var panel in sourceBuilding.Panels.Items) {
                var panelAxis = panel.Value.ToLine();
                panelAxis.Transform(transformMatrix);
                transformedBuilding.Panels.Items[panel.Key].SetAxis(panelAxis);
            }

            foreach (var space in sourceBuilding.Spaces) {
                var spaceOutline = space.Value.ToPolyline();
                spaceOutline.Transform(transformMatrix);
                transformedBuilding.Spaces[space.Key].SetCoordinates(spaceOutline);
            }

            if (sourceBuilding.AppliedTransformMatrix != null) {
                Transform previousMatrix = sourceBuilding.GetAppliedTransformMatrix();
                Transform finalTransform = transformMatrix * previousMatrix;
                if (finalTransform.TryGetInverse(out Transform toGetBack)) {
                    transformedBuilding.SaveTransformMatrixToTheOriginal(toGetBack);
                }
                transformedBuilding.SaveAppliedTransformMatrix(finalTransform);
            }
            else {
                if (transformMatrix.TryGetInverse(out Transform toGetBack)) {
                    transformedBuilding.SaveTransformMatrixToTheOriginal(toGetBack);
                }
                transformedBuilding.SaveAppliedTransformMatrix(transformMatrix);
            }
            return transformedBuilding;
        }

    }
}
